; ============================================================================
; reports/VendorReceiving.ahk — WRITE handler: create a Bravo vendor receiving
;
; First write-side module in the pipeline. Drives Bravo POS through the
; Inventory → Stock Management → Add Receiving flow → Item Inventory tab →
; per-unit Add General Merchandise → Save → capture RI-VP number.
;
; HISTORY:
;   v1 (2026-05-22 morning, REMOVED): tried Stock Inventory tab → Create
;     Bucket. The new-inv-intake SKILL.md said that was the validated path
;     against M&M #31152 — turned out to be wrong. Bucket dialog's field
;     lookups by label Name picked up Text labels (not Edit fields), and
;     the items never actually got their values stored.
;   v2 (2026-05-22 afternoon, THIS FILE): rewritten after Joshua manually
;     walked the correct flow during the #31237 entry. Item Inventory tab,
;     Add General Merchandise per unit, Copy Item to duplicate within a SKU,
;     per-row Location set to SALESFLOOR.
;
; THE FLOW (validated against #31237 at CUL on 2026-05-22):
;   1. EnsureStore(store) — switch Bravo to target store via SwitchStore
;   2. BackToDashboard + DismissPopups
;   3. Inventory (right sidebar)
;   4. Stock Management (right sidebar)
;   5. Add Receiving (right sidebar)
;   6. Select Vendor → paste Business Name → Search → Select → Ok
;   7. Click Item Inventory tab (NOT Stock Inventory)
;   8. For each SKU/line in the payload:
;      a. Click Add General Merchandise — creates a new row, qty 1
;      b. Click Item view (so the detail panel is visible)
;      c. Click Edit next to Category — opens Select Category dialog
;      d. Click the category leaf (e.g. Sporting Goods at top level)
;      e. Click Ok on category dialog
;      f. Triple-click Tag Description, paste the item description
;      g. Triple-click Cost field, paste cost, Tab
;      h. Triple-click MSRP field, paste msrp, Tab
;      i. Triple-click Price field, paste price, Tab
;      j. Click Location dropdown, pick SALESFLOOR
;      k. For each additional unit of this SKU (qty - 1 times):
;         - Click Copy Item — duplicates the row except Location
;         - Click new row in the grid
;         - Click Location dropdown, pick SALESFLOOR
;   9. Triple-click Invoice Number (header field), paste invoice #
;   10. Triple-click Shipping, paste shipping, Tab
;   11. Triple-click Tax (only if > 0), paste tax, Tab
;   12. Click Save → wait 8-10s for Print Tags dialog
;   13. Click Ok on Print Tags dialog to skip printing
;   14. Navigate to Stock Management list (Bravo lands there automatically)
;   15. Read top row's Number column to capture RI-VP######## receiving number
;
; KEY UI QUIRKS LEARNED:
; - Bravo's field labels and edit fields are SEPARATE UIA elements. FindByName
;   returns the label Text, not the underlying Edit. So we use coordinate-based
;   triple-click + clipboard paste for ALL field edits. UIA is reserved for
;   buttons and navigation elements (which expose unique Names).
; - Category tree is FLAT in the Item Inventory bucket — "Sporting Goods" is
;   a TOP-LEVEL entry, not nested under "Manufactured Goods". (The Stock
;   Inventory bucket dialog had it nested; Item Inventory does not.)
; - Location field is REQUIRED per item. Save shows red ❌ on the field if
;   missing. Setting Location once on a Copy Item-duplicated row does NOT
;   carry to its copies — each row needs its own Location set.
; - BRAVO_WIN_TITLE = "Bravo " collides with File Explorer when the project
;   folder is open. This handler overrides to "VALLEY PAWN" at entry. (See
;   smoke driver for context.)
; - Store row UIA Name in Global Access is "VALLEY PAWN - CULPEPER" (full
;   format), not "Culpeper". SC_STORE_FULL_NAME in lib/StoreCycle.ahk has
;   the wrong values — patched in this file's PullVendorReceiving entry.
;
; Two entry points:
;   PullVendorReceiving(store, payload, outputDir)
;     — direct-call API. `payload` is an AHK Map. Used by the smoke driver.
;   PullVendorReceivingFromSidecar(store, payloadKey, outputDir)
;     — watcher-friendly API. Reads triggers/payloads/<store>_<key>.payload.json
;       and forwards to PullVendorReceiving.
;
; Payload schema (also documented in vendor_receiving_smoke.ahk):
;   {
;     "store":           "CUL",
;     "dry_run":         true,             // skip Save, leave form filled
;     "vendor":          "M&M Merchandisers",
;     "invoice_number":  "31237",
;     "invoice_date":    "2026-05-20",     // YYYY-MM-DD (currently unused — defaults to today)
;     "shipping":        10.05,
;     "tax":             0.00,
;     "lines": [
;       {
;         "vendor_sku":        "S1005-BK",         // for reference; goes into reference_number if set
;         "description_bravo": "SABRE 600K MINI STUN BLACK",   // <=32 chars
;         "qty":               3,                  // number of units to create as individual items
;         "unit_cost":         13.99,
;         "msrp":              27.98,
;         "price":             27.98,
;         "category_path":     ["Sporting Goods"], // FLAT in Item Inventory
;         "location":          "SALESFLOOR"        // default if omitted
;       },
;       ...
;     ]
;   }
;
; Result envelope:
;   report:            "vendor-receiving"
;   store:             "CUL"
;   date:              <invoice_number>
;   status:            "success" | "dry_run" | "skipped_idempotent" | "error"
;   output_path:       ""
;   row_count:         <sum of all qty across lines>
;   duration_ms:       <int>
;   error:             <string>
;   receiving_number:  "RI-VP4000273"
;   item_numbers:      [array of VP######### item numbers in creation order]
;   dry_run:           true|false
; ============================================================================

#Requires AutoHotkey v2.0

; ----- UIA Name constants (for buttons / navigation — verified 2026-05-22) ---

global VR_ELEMENTS := Map(
    ; Dashboard sidebar / Inventory module navigation
    "sidebar_inventory",         "Inventory",
    "panel_stock_management",    "Stock Management",
    "panel_add_receiving",       "Add Receiving",

    ; Vendor selection
    "btn_select_vendor",         "Select Vendor",
    "field_business_name",       "Business Name",
    "btn_vendor_search",         "Search",
    "btn_vendor_select",         "Select",
    "btn_vendor_ok",             "Ok",

    ; Item Inventory tab + add buttons
    "tab_item_inventory",        "Item Inventory",
    "btn_add_general_merch",     "Add General Merchandise",
    "btn_item_view",             "Item view",
    "btn_copy_item",             "Copy Item",

    ; Category dialog
    "btn_edit_category",         "Edit",       ; ⚠ generic, may collide
    "btn_category_ok",           "Ok",

    ; Save + post-Save
    "btn_save",                  "Save",
    "btn_print_tags_ok",         "Ok"
)

; Pixel-coord targets validated against CUL on 2026-05-22.
; These cover the cases where UIA Names don't uniquely identify the target
; (mostly the Item view detail-panel fields which are inside DevExpress
; controls with generic Names like "BravoMaskedTextBox").
;
; Coordinates are SCREEN-space — CoordMode Mouse/Pixel = Screen is set in
; lib/Bravo.ahk. CUL's Bravo window was at fullscreen-ish; if these miss on
; other stores, capture a UIADiscover dump and re-tune.
global VR_COORDS := Map(
    ; Receiving form — tabs and buttons
    "tab_item_inventory",     Map("x",  506, "y", 207),
    "btn_add_general_merch",  Map("x", 1040, "y", 227),
    "btn_item_view",          Map("x",  209, "y", 688),
    "btn_edit_category",      Map("x",  305, "y", 338),
    "btn_copy_item",          Map("x",  265, "y", 661),

    ; Item detail panel (left side, when Item view is active)
    "field_tag_description",  Map("x",  208, "y", 410),
    "field_msrp",             Map("x",  135, "y", 481),
    "field_price",            Map("x",  207, "y", 481),
    "field_cost",             Map("x",  285, "y", 481),
    "field_location_arrow",   Map("x",  206, "y", 445),
    "loc_dropdown_salesfloor",Map("x",  136, "y", 531),

    ; Header (bottom right of Receiving form)
    "field_invoice_number",   Map("x",  870, "y", 663),
    "field_shipping",         Map("x",  870, "y", 521),
    "field_tax",              Map("x",  870, "y", 593),

    ; Save + post-Save
    "btn_save",               Map("x", 1108, "y", 165),
    "btn_print_tags_ok",      Map("x",  851, "y", 603),

    ; Item Inventory grid — first row's Y, plus row pitch for additional rows
    ; Used after Copy Item to select the newly-added row and re-set Location.
    "grid_row1_y",            Map("x",  640, "y", 250),
    ; Distance in pixels between consecutive grid rows
    "grid_row_pitch_y",       Map("x",  0,   "y",  23)
)

; ----- Public API ------------------------------------------------------------

PullVendorReceiving(store, payload, outputDir) {
    started := A_TickCount

    ; --- Patch global title to avoid File Explorer collision ----------------
    ; lib/Bravo.ahk sets BRAVO_WIN_TITLE := "Bravo " — that string is also
    ; a prefix of File Explorer's "Bravo Data Extraction" window title, and
    ; AHK WinExist will lock onto whichever matches first. Switching to
    ; "VALLEY PAWN" (Bravo POS title suffix, never appears in File Explorer)
    ; is unambiguous.
    global BRAVO_WIN_TITLE
    BRAVO_WIN_TITLE := "VALLEY PAWN"

    ; --- Patch StoreCycle store-row UIA Names -------------------------------
    ; Global Access store rows expose Names like "VALLEY PAWN - CULPEPER",
    ; NOT "Culpeper". Update the map so EnsureStore can find them. Idempotent
    ; — overwriting with the same values does nothing.
    global SC_STORE_FULL_NAME
    SC_STORE_FULL_NAME["CUL"] := "VALLEY PAWN - CULPEPER"
    SC_STORE_FULL_NAME["HAR"] := "VALLEY PAWN - HARRISONBURG"
    SC_STORE_FULL_NAME["LEX"] := "VALLEY PAWN - LEXINGTON"
    SC_STORE_FULL_NAME["ROA"] := "VALLEY PAWN - ROANOKE"
    SC_STORE_FULL_NAME["WAY"] := "VALLEY PAWN - WAYNESBORO"

    ; --- Parse payload ------------------------------------------------------
    invoiceNumber := payload.Has("invoice_number") ? payload["invoice_number"] : ""
    vendor        := payload.Has("vendor")         ? payload["vendor"]         : ""
    dryRun        := payload.Has("dry_run")        ? payload["dry_run"]        : true
    lines         := payload.Has("lines")          ? payload["lines"]          : []
    shipping      := payload.Has("shipping")       ? payload["shipping"]       : 0.00
    tax           := payload.Has("tax")            ? payload["tax"]            : 0.00

    totalQty := 0
    for line in lines
        totalQty += (line.Has("qty") ? line["qty"] : 1)

    result := Map(
        "report",           "vendor-receiving",
        "store",            store,
        "date",             invoiceNumber,
        "status",           "error",
        "output_path",      "",
        "row_count",        totalQty,
        "duration_ms",      0,
        "error",            "",
        "receiving_number", "",
        "item_numbers",     [],
        "dry_run",          dryRun ? true : false
    )

    LogMessage("[" . store . "] VendorReceiving v2 vendor='" . vendor . "' invoice='" . invoiceNumber . "' lines=" . lines.Length . " units=" . totalQty . " dry_run=" . (dryRun ? "true" : "false"))

    ; --- Validate payload ---------------------------------------------------
    if (vendor = "")
        return Fail(result, started, "payload.vendor is empty")
    if (invoiceNumber = "")
        return Fail(result, started, "payload.invoice_number is empty")
    if (lines.Length = 0)
        return Fail(result, started, "payload.lines is empty (nothing to receive)")
    if (totalQty = 0)
        return Fail(result, started, "no units to create (every line has qty=0)")

    ; --- Standard prelude ---------------------------------------------------
    if !WaitForBravoWindowExists(30)
        return Fail(result, started, "Bravo window not found within 30s")
    ActivateBravo()
    DismissPopups()

    global CONFIG
    password := CONFIG.Has("bravo.password") ? CONFIG["bravo.password"] : ""
    if !EnsureStore(store, password)
        return Fail(result, started, "EnsureStore failed for " . store)
    LogMessage("  store confirmed: " . store)

    if !BackToDashboard()
        return Fail(result, started, "BackToDashboard could not return Bravo to Dashboard")
    Sleep(500)
    DismissPopups()

    ; --- Navigate to Add Receiving form ------------------------------------
    try {
        LogMessage("  step 1: open Inventory module")
        ClickByName(VR_ELEMENTS["sidebar_inventory"], 8000)
        Sleep(2000)
        DismissPopups()

        LogMessage("  step 2: open Stock Management")
        ClickByName(VR_ELEMENTS["panel_stock_management"], 8000)
        Sleep(2000)
        DismissPopups()

        LogMessage("  step 3: click Add Receiving")
        ClickByName(VR_ELEMENTS["panel_add_receiving"], 8000)
        Sleep(4000)
        DismissPopups()
    } catch as e {
        LogVisibleNames()
        return Fail(result, started, "Navigation to Add Receiving failed: " . e.Message)
    }

    ; --- Select vendor ------------------------------------------------------
    try {
        LogMessage("  step 4: click Select Vendor")
        ClickByName(VR_ELEMENTS["btn_select_vendor"], 5000)
        Sleep(2000)

        LogMessage("  step 5: paste vendor name '" . vendor . "' into Business Name")
        ClickByName(VR_ELEMENTS["field_business_name"], 4000)
        Sleep(300)
        Send("^a")
        Sleep(80)
        VrPaste(vendor)
        Sleep(500)

        LogMessage("  step 6: click Search")
        ClickByName(VR_ELEMENTS["btn_vendor_search"], 4000)
        Sleep(3000)

        LogMessage("  step 7: click Select")
        ClickByName(VR_ELEMENTS["btn_vendor_select"], 5000)
        Sleep(1500)

        LogMessage("  step 8: click Ok (vendor confirm)")
        ClickByName(VR_ELEMENTS["btn_vendor_ok"], 5000)
        Sleep(2000)
    } catch as e {
        LogVisibleNames()
        return Fail(result, started, "Vendor selection failed for '" . vendor . "': " . e.Message . " (does the vendor exist at this store's Bravo? Each store has its own vendor list. Auto-create via Add New Vendor is a Phase 6 follow-up.)")
    }

    ; --- Switch to Item Inventory tab --------------------------------------
    try {
        LogMessage("  step 9: click Item Inventory tab")
        VrClickAt("tab_item_inventory")
        Sleep(1500)
    } catch as e {
        return Fail(result, started, "Item Inventory tab click failed: " . e.Message)
    }

    ; --- Add line items, one Item Inventory row per unit -------------------
    itemNumbers := []
    rowsCreatedSoFar := 0
    lineIndex := 0
    for line in lines {
        lineIndex += 1
        sku := line.Has("vendor_sku") ? line["vendor_sku"] : ""
        descBravo := line.Has("description_bravo") ? line["description_bravo"] : ""
        qty := line.Has("qty") ? line["qty"] : 1
        unitCost := line.Has("unit_cost") ? line["unit_cost"] : 0.00
        msrp := line.Has("msrp") ? line["msrp"] : 0.00
        price := line.Has("price") ? line["price"] : 0.00
        categoryPath := line.Has("category_path") ? line["category_path"] : ["Sporting Goods"]
        location := line.Has("location") ? line["location"] : "SALESFLOOR"

        LogMessage("  --- line " . lineIndex . "/" . lines.Length . ": sku='" . sku . "' desc='" . descBravo . "' qty=" . qty . " unit=$" . unitCost)

        if (StrLen(descBravo) > 32) {
            LogMessage("    WARN: description_bravo is " . StrLen(descBravo) . " chars (Bravo's 32-char cap will truncate)")
        }

        ; -- Unit 1 of this SKU: full Add General Merchandise + fill flow --
        try {
            LogMessage("    unit 1: Add General Merchandise")
            VrClickAt("btn_add_general_merch")
            Sleep(2000)

            LogMessage("    unit 1: Item view (open detail panel)")
            VrClickAt("btn_item_view")
            Sleep(1500)

            ; Category
            LogMessage("    unit 1: Edit category")
            VrClickAt("btn_edit_category")
            Sleep(2000)
            ; In Item Inventory's category dialog, categories are FLAT —
            ; click the leaf directly. If the path has multiple levels we
            ; expand each; last entry is the leaf to select.
            VrPickCategoryFlat(categoryPath)
            Sleep(500)
            LogMessage("    unit 1: click category Ok")
            ; Category dialog Ok lives by Name "Ok" — multiple Oks may match;
            ; rely on the dialog being focused so its Ok is the topmost match.
            ClickByName(VR_ELEMENTS["btn_category_ok"], 4000)
            Sleep(2000)

            ; Tag Description
            LogMessage("    unit 1: paste Tag Description")
            VrTriplePaste("field_tag_description", descBravo)
            Sleep(300)

            ; Cost
            LogMessage("    unit 1: paste Cost = " . unitCost)
            VrTriplePaste("field_cost", Format("{:.2f}", unitCost))
            Send("{Tab}")
            Sleep(200)

            ; MSRP
            LogMessage("    unit 1: paste MSRP = " . msrp)
            VrTriplePaste("field_msrp", Format("{:.2f}", msrp))
            Send("{Tab}")
            Sleep(200)

            ; Price
            LogMessage("    unit 1: paste Price = " . price)
            VrTriplePaste("field_price", Format("{:.2f}", price))
            Send("{Tab}")
            Sleep(200)

            ; Location — click the dropdown ARROW (right edge of field) so
            ; the dropdown opens, then click SALESFLOOR (or the requested
            ; location).
            LogMessage("    unit 1: set Location = " . location)
            VrSetLocation(location)
            Sleep(500)

            rowsCreatedSoFar += 1
            itemNumbers.Push("pending")   ; placeholder — actual number assigned at Save

            ; -- Units 2..qty: Copy Item then set Location -----------------
            ; Copy Item duplicates the currently-selected row except Location.
            ; We then click the new (copied) row in the grid and re-set Location.
            Loop (qty - 1) {
                unitN := A_Index + 1
                LogMessage("    unit " . unitN . ": Copy Item")
                VrClickAt("btn_copy_item")
                Sleep(2000)
                rowsCreatedSoFar += 1
                itemNumbers.Push("pending")

                ; The newly-copied row appears in the grid. Bravo's grid sort
                ; order varies; after Copy the new row may be at the top or
                ; bottom. We rely on the detail panel showing the NEW row
                ; (Copy auto-selects the new one), so the Location field on
                ; the panel maps to the new row.
                LogMessage("    unit " . unitN . ": set Location on copy")
                VrSetLocation(location)
                Sleep(400)
            }
        } catch as e {
            LogVisibleNames()
            return Fail(result, started, "Line " . lineIndex . " (sku=" . sku . ") failed at unit creation: " . e.Message)
        }
    }
    result["item_numbers"] := itemNumbers

    ; --- Fill header fields -------------------------------------------------
    try {
        LogMessage("  header: Invoice Number = " . invoiceNumber)
        VrTriplePaste("field_invoice_number", invoiceNumber)
        Send("{Tab}")
        Sleep(300)

        LogMessage("  header: Shipping = " . shipping)
        VrTriplePaste("field_shipping", Format("{:.2f}", shipping))
        Send("{Tab}")
        Sleep(400)

        if (tax > 0) {
            LogMessage("  header: Tax = " . tax)
            VrTriplePaste("field_tax", Format("{:.2f}", tax))
            Send("{Tab}")
            Sleep(400)
        }
    } catch as e {
        LogVisibleNames()
        return Fail(result, started, "Header field fill failed: " . e.Message)
    }

    ; --- Dry-run stop --------------------------------------------------------
    if (dryRun) {
        LogMessage("  DRY-RUN: form populated with " . rowsCreatedSoFar . " items, stopping before Save.")
        result["status"] := "dry_run"
        result["duration_ms"] := A_TickCount - started
        return result
    }

    ; --- Save ----------------------------------------------------------------
    try {
        LogMessage("  step S: click Save")
        VrClickAt("btn_save")
        Sleep(8000)
        DismissPopups()

        LogMessage("  step S+1: dismiss Print Tags dialog (Ok)")
        VrClickAt("btn_print_tags_ok")
        Sleep(3000)

        ; --- Capture RI-VP receiving number from Stock Management list ----
        ; After Print Tags Ok, Bravo lands on Stock Management with the
        ; receivings list. Our new receiving is the top row. Walk visible
        ; Text elements and grab the first matching RI-VP######### pattern.
        try {
            riNum := ""
            root := GetBravoRoot()
            for typeName in ["DataItem", "Text", "Hyperlink"] {
                try {
                    elems := root.FindElements({Type: typeName})
                    for elem in elems {
                        try {
                            n := elem.Name
                            if RegExMatch(n, "i)\bRI-V[AP]+\d{6,}\b", &m) {
                                riNum := m[0]
                                break 2
                            }
                        }
                    }
                }
            }
            if (riNum != "") {
                result["receiving_number"] := riNum
                LogMessage("  CAPTURED receiving_number=" . riNum)
            } else {
                LogMessage("  WARN: RI-VP capture failed; operator should read it manually from Stock Mgmt list (top row)")
            }
        } catch as e {
            LogMessage("  WARN: RI-VP capture threw: " . e.Message)
        }
    } catch as e {
        LogVisibleNames()
        return Fail(result, started, "Save / post-Save handling failed: " . e.Message)
    }

    result["status"] := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS receiving_number=" . result["receiving_number"] . " units=" . rowsCreatedSoFar . " " . result["duration_ms"] . "ms")
    return result
}

; ----- Watcher-friendly sidecar entry ---------------------------------------

PullVendorReceivingFromSidecar(store, payloadKey, outputDir) {
    started := A_TickCount
    global CONFIG
    triggersDir := CONFIG.Has("paths.triggers") ? CONFIG["paths.triggers"] : (A_ScriptDir . "\triggers")
    sidecarPath := triggersDir . "\payloads\" . store . "_" . payloadKey . ".payload.json"

    if !FileExist(sidecarPath) {
        return Fail(Map(
            "report",      "vendor-receiving",
            "store",       store,
            "date",        payloadKey,
            "status",      "error",
            "output_path", "",
            "row_count",   0,
            "duration_ms", 0,
            "error",       ""
        ), started, "payload sidecar not found at " . sidecarPath)
    }

    LogMessage("[" . store . "] sidecar load: " . sidecarPath)
    payload := VrParsePayloadJson(FileRead(sidecarPath, "UTF-8"))
    return PullVendorReceiving(store, payload, outputDir)
}

; ----- Internal helpers ------------------------------------------------------

; Coordinate-based click using VR_COORDS[key]. Throws if the key isn't mapped.
VrClickAt(key) {
    if !VR_COORDS.Has(key)
        throw Error("VrClickAt: unknown coord key '" . key . "'")
    coord := VR_COORDS[key]
    Click(coord["x"] . " " . coord["y"])
}

; Triple-click a field by VR_COORDS key, then paste the value via clipboard.
; This is the canonical field-edit approach for the Item view detail panel
; (where UIA finds Text labels not Edit fields). Triple-click selects existing
; cell contents so paste overwrites cleanly.
VrTriplePaste(coordKey, value) {
    if !VR_COORDS.Has(coordKey)
        throw Error("VrTriplePaste: unknown coord key '" . coordKey . "'")
    coord := VR_COORDS[coordKey]
    Click(coord["x"] . " " . coord["y"])
    Sleep(120)
    Click(coord["x"] . " " . coord["y"])
    Sleep(120)
    Click(coord["x"] . " " . coord["y"])
    Sleep(250)
    VrPaste(value)
}

; Paste a string via clipboard + Ctrl+V. Required path on the Parallels VM
; (the `type` tool has a runaway-character bug). Restores clipboard after.
VrPaste(value) {
    prev := ""
    try prev := A_Clipboard
    A_Clipboard := value
    if !ClipWait(2)
        throw Error("VrPaste: clipboard did not receive value '" . SubStr(String(value), 1, 40) . "'")
    Send("^v")
    Sleep(250)
    A_Clipboard := prev
}

; Set the Location field on the currently-selected Item view row.
; The dropdown shows 5 options (BROKEN, EBAY, MISSING, SALESFLOOR, SCRAP).
; SALESFLOOR is the standard for newly-received GM items at any store.
; Other values pass through unchanged.
VrSetLocation(value := "SALESFLOOR") {
    ; Click the dropdown arrow (right edge of the Location combo box).
    VrClickAt("field_location_arrow")
    Sleep(400)
    ; SALESFLOOR is at the validated coordinate. For other values we'd
    ; need to map their dropdown positions; this is a TODO if the store
    ; ever needs items routed to a different Location at receiving time.
    if (value = "SALESFLOOR") {
        VrClickAt("loc_dropdown_salesfloor")
    } else {
        LogMessage("    WARN: Location='" . value . "' not in coord map; defaulting to SALESFLOOR")
        VrClickAt("loc_dropdown_salesfloor")
    }
    Sleep(300)
}

; Pick a category in the flat Item-Inventory category dialog. The dialog
; shows top-level entries like Jewelry, Manufactured Goods, Electronics,
; Sporting Goods, etc. Most categories ARE the leaf (single-level path);
; if the payload's category_path has multiple levels, we walk and expand.
VrPickCategoryFlat(path) {
    if (path.Length = 0) {
        LogMessage("    WARN: category_path empty — item will land in default Miscellaneous")
        return
    }
    for i, label in path {
        isLeaf := (i = path.Length)
        LogMessage("    [cat] level " . i . " '" . label . "' (leaf=" . (isLeaf ? "yes" : "no") . ")")
        elem := FindByName(label, 6000)
        if !elem {
            LogVisibleNames()
            throw Error("VrPickCategoryFlat: category '" . label . "' not found at level " . i)
        }
        if (!isLeaf) {
            ; Multi-level path — expand
            expanded := false
            try {
                elem.ExpandCollapsePattern.Expand()
                expanded := true
            }
            if (!expanded) {
                try elem.Click("left")
            }
            Sleep(500)
        } else {
            ; Leaf — select
            try {
                elem.Click("left")
            } catch as e {
                throw Error("VrPickCategoryFlat: leaf click failed for '" . label . "': " . e.Message)
            }
            Sleep(400)
        }
    }
}

; ----- Minimal JSON parser for payload sidecars -----------------------------

VrParsePayloadJson(text) {
    payload := Map()
    payload["lines"] := []
    for key in ["store", "vendor", "invoice_number", "invoice_date"] {
        if RegExMatch(text, '"' . key . '"\s*:\s*"([^"]*)"', &m)
            payload[key] := m[1]
    }
    for key in ["shipping", "tax"] {
        if RegExMatch(text, '"' . key . '"\s*:\s*([-\d.]+)', &m)
            payload[key] := m[1] + 0.0
    }
    if RegExMatch(text, '"dry_run"\s*:\s*(true|false)', &m)
        payload["dry_run"] := (m[1] = "true")
    ; Match the lines array. Two challenges:
    ; 1. AHK `.` doesn't match newlines by default — use [\s\S] (any char)
    ;    in character class (which DOES match newlines).
    ; 2. Lines values contain inner `]` (e.g. "category_path": ["Sporting Goods"]).
    ;    A lazy match terminated on `\]\s*[,}]` would stop on the inner `]`.
    ;    Use a GREEDY match anchored to the closing of the JSON object: the
    ;    outer `]\s*\}` is unambiguous (relies on `lines` being the last
    ;    top-level key in the payload schema, which it always is by convention).
    if RegExMatch(text, '"lines"\s*:\s*\[([\s\S]*)\]\s*\}', &lm) {
        linesText := lm[1]
        pos := 1
        while RegExMatch(linesText, '\{[^{}]*\}', &block, pos) {
            blockText := block[0]
            line := Map()
            for key in ["vendor_sku", "description_bravo", "location"] {
                if RegExMatch(blockText, '"' . key . '"\s*:\s*"([^"]*)"', &bm)
                    line[key] := bm[1]
            }
            if RegExMatch(blockText, '"qty"\s*:\s*(\d+)', &bm)
                line["qty"] := Integer(bm[1])
            for key in ["unit_cost", "msrp", "price"] {
                if RegExMatch(blockText, '"' . key . '"\s*:\s*([-\d.]+)', &bm)
                    line[key] := bm[1] + 0.0
            }
            if RegExMatch(blockText, '"category_path"\s*:\s*\[([^\]]*)\]', &bm) {
                cats := []
                cp := 1
                while RegExMatch(bm[1], '"([^"]*)"', &cm, cp) {
                    cats.Push(cm[1])
                    cp := cm.Pos + cm.Len
                }
                line["category_path"] := cats
            }
            payload["lines"].Push(line)
            pos := block.Pos + block.Len
        }
    }
    return payload
}
