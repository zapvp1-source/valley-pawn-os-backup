; ============================================================================
; reports/ItemsToPrice.ahk
;
; Dumps the full "Items to Price" worklist (inventory items pulled from
; defaulted loans or bought from the public that are available to sell but have
; not yet been priced / put on the floor — Status = UNPRICED) for one store to
; a CSV, using the production-proven shared grid walker WriteBuysGridToCsv().
;
; Bravo surfaces this worklist as the Dashboard "Price Items" quick-action
; button (with a red count badge). Clicking it opens the Inventory module
; filtered to exactly those unpriced items. We then walk EVERY row to CSV — the
; same DataItem-based walker the inventory / loan-portfolio handlers use, which
; reliably captures all rows of a virtualized Bravo grid. The downstream
; daily-items-to-price task computes the per-store COUNT (rows) and DOLLAR
; (sum of the Cost column) from this CSV — no fragile in-handler scrolling math.
;
; SKILL it powers: daily-items-to-price (8 AM ET, posts count + $ by store)
;
; UI path:
;   Dashboard -> "Price Items" button (center grid, carries count badge)
;   -> Inventory working view (DataItem grid of the unpriced items)
;   -> WriteBuysGridToCsv() pages the whole grid to CSV
;   -> Done button -> back to Dashboard
;
; Output CSV: the full grid dump — header is the grid's column labels
;   (Number, Status, Category, Type, Description, Location, Cost, Date),
;   one row per unpriced item. Cost values look like "$714.00".
;
; ADDITIVE — reuses the shared WriteBuysGridToCsv()/WaitForBravoWindowExists()
; helpers. Defines only the uniquely-named IsOnDashboardITP() local helper.
; ============================================================================

#Requires AutoHotkey v2.0

global ITEMS_TO_PRICE_ELEMENTS := Map(
    "dashboard_button", "Price Items",
    "exit_done",        "Done"
)

PullItemsToPrice(store, date, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "items-to-price",
        "store",       store,
        "date",        date,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    outputPath := outputDir . "\" . OutputFilename(date, store, "items-to-price")
    LogMessage("[" . store . "] ItemsToPrice date=" . date . " -> " . outputPath)

    if !WaitForBravoWindowExists(30)
        return Fail(result, started, "Bravo window not found within 30s")

    ActivateBravo()
    DismissPopups()

    global CONFIG
    password := CONFIG.Has("bravo.password") ? CONFIG["bravo.password"] : ""
    if !EnsureStore(store, password)
        return Fail(result, started, "EnsureStore failed for " . store)
    LogMessage("  store confirmed: " . store)

    ResetOutputFile(outputPath)

    ; Get to the Dashboard. The Inventory working view exits via "Done"; the
    ; generic BackToDashboard clicks "Cancel" which can't leave that view, so if
    ; it fails, click Done (to clear a possibly-stuck Inventory view) and retry.
    if !BackToDashboard() {
        LogMessage("  start: BackToDashboard failed — clicking Done in case stuck in Inventory view")
        try ClickByName(ITEMS_TO_PRICE_ELEMENTS["exit_done"], 3000)
        Sleep(1500)
        DismissPopups()
        if !IsOnDashboardITP() && !BackToDashboard()
            return Fail(result, started, "BackToDashboard could not return Bravo to Dashboard")
    }
    Sleep(500)
    DismissPopups()

    rowsWritten := 0
    try {
        DismissPopups()

        ; (added 2026-06-22) Open the Price Items view and wait for it to be
        ; READY, with up to 3 attempts. "Ready" = either DataItem rows rendered,
        ; OR Bravo's "Price Items: N" header counter confirms N=0 (truly empty).
        ; A cold/just-updated Bravo can take >90s to draw the grid; rather than
        ; mistake that slow render for "0/failed", we re-open the view and wait
        ; again. Only after all attempts (counter shows items but no rows ever
        ; draw, or no counter at all) is it a genuine render failure.
        gridReady := false
        emptyWorklist := false
        cntLabel := ""
        ATTEMPTS := 3
        Loop ATTEMPTS {
            tryNum := A_Index
            if (tryNum > 1) {
                LogMessage("  step 1 (retry " . tryNum . "/" . ATTEMPTS . "): re-opening Price Items view")
                DismissPopups()
                if !IsOnDashboardITP()
                    BackToDashboard()
                Sleep(1000)
            } else {
                LogMessage("  step 1: click Dashboard 'Price Items' button")
            }
            try ClickByName(ITEMS_TO_PRICE_ELEMENTS["dashboard_button"], 8000)

            LogMessage("  step 2 (attempt " . tryNum . "): wait up to 90s for rows OR a confirmed 'Price Items: 0'")
            waitStart := A_TickCount
            cntLabel := ""
            Loop {
                try {
                    root := GetBravoRoot()
                    di := root.FindElements({Type: "DataItem"})
                    if (di && di.Length > 0) {
                        LogMessage("    [grid] rendered with " . di.Length . " initial DataItems after " . ((A_TickCount - waitStart) // 1000) . "s (attempt " . tryNum . ")")
                        gridReady := true
                        break
                    }
                    ; read the header counter each poll — a CONFIRMED 0 = truly
                    ; empty. (2026-06-25) Scan ALL common element types, not just
                    ; "Text": Bravo renders the "Price Items: N" header as a
                    ; NON-Text node when the worklist is empty, so the old
                    ; Text-only scan missed "Price Items: 0" and an empty store
                    ; looked like a render failure (burned the 3x90s retry loop
                    ; and was reported MISSING). Headless — no screenshot needed.
                    cntLabel := ReadPriceItemsCounterITP(root)
                    if (cntLabel = "0") {
                        LogMessage("    [grid] header counter reads 'Price Items: 0' -> EMPTY worklist (attempt " . tryNum . ")")
                        emptyWorklist := true
                        break
                    }
                }
                if (A_TickCount - waitStart > 90000)
                    break
                Sleep(2000)
            }
            if (gridReady || emptyWorklist)
                break
            LogMessage("    [grid] not ready after 90s (counter='" . cntLabel . "') -> " . (tryNum < ATTEMPTS ? "retrying" : "out of attempts"))
        }
        if (!gridReady && !emptyWorklist) {
            LogVisibleNames()
            throw Error("Price Items grid did not render after " . ATTEMPTS . " attempts (last counter='" . cntLabel . "')")
        }

        if (emptyWorklist) {
            ; Header-only CSV so downstream parses a present, zero-row file
            ; (count=0), never MISSING. Header matches the populated-store dump.
            try FileAppend("Number,Status,Category,Type,Description,Location,Cost,Date`r`n", outputPath, "UTF-8-RAW")
            rowsWritten := 0
            LogMessage("    wrote header-only CSV (0 unpriced rows) for empty worklist")
        } else {
            Sleep(3000)  ; let the grid settle before walking
            DismissPopups()

            ; --- Dump EVERY unpriced row to CSV --------------------------------
            ; The Price Items grid loads in ~60-row batches and needs a "Show More"
            ; click to pull each next batch, so we use the Show-More-aware walker
            ; (WriteInventoryGridWithShowMore) rather than WriteBuysGridToCsv, which
            ; stops at the first batch. Scroll to the very top first so the walk
            ; starts from row 1.
            LogMessage("  step 3a: scroll grid to top before walking")
            try {
                root := GetBravoRoot()
                firstDi := root.FindElement({Type: "DataItem"})
                if firstDi {
                    try firstDi.Click("left")
                    Sleep(300)
                    Send("^{Home}")
                    Sleep(800)
                }
            }
            LogMessage("  step 3b: walk grid (PageDown + Show More) and write CSV")
            rowsWritten := WriteInventoryGridWithShowMore(outputPath)
            if (rowsWritten < 0) {
                LogVisibleNames()
                throw Error("WriteInventoryGridWithShowMore returned -1 (no rows / no columns captured)")
            }
            LogMessage("    wrote " . rowsWritten . " unpriced rows to CSV")
        }

        ; --- Exit back to Dashboard via "Done" ------------------------------
        exited := false
        Loop 3 {
            try ClickByName(ITEMS_TO_PRICE_ELEMENTS["exit_done"], 4000)
            Sleep(1500)
            DismissPopups()
            if IsOnDashboardITP() {
                exited := true
                break
            }
        }
        if !exited {
            LogMessage("    WARN: Dashboard not confirmed after Done x3 — trying BackToDashboard")
            try BackToDashboard()
        }
        Sleep(500)
    } catch as e {
        LogVisibleNames()
        return Fail(result, started, "UIA click sequence failed: " . e.Message)
    }

    result["row_count"]   := rowsWritten
    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: rows=" . rowsWritten . ", " . result["duration_ms"] . "ms")
    return result
}

; ---------------------------------------------------------------------------
; Read Bravo's "Price Items: N" worklist header counter. Returns the count as a
; string ("0".."N"), or "" if no header is present yet. (added 2026-06-25)
;
; Why this exists: when the worklist is EMPTY, Bravo renders the header as a
; SPLIT pair of UIA nodes — a label "Price Items:" and the number ("0") in a
; SEPARATE sibling node (confirmed via live counter-diag on ROA 2026-06-25). A
; single-node "Price Items:\s*(\d+)" regex therefore never matched, so an empty
; store looked identical to a slow/failed render — burning the 3x90s retry loop
; and ultimately being reported MISSING. This reads the split count too, so an
; empty store is confirmed as 0 fully headlessly (no screenshot / no operator)
; and the handler writes a header-only zero CSV. Safe against false 0s:
; populated stores render DataItem rows (checked first by the caller), so this
; only ever runs / confirms 0 when the grid is genuinely empty.
; ---------------------------------------------------------------------------
ReadPriceItemsCounterITP(root) {
    static TYPES := ["Text","Group","Pane","Custom","Header","HeaderItem","Document","Image","DataItem","ListItem","Button","Edit","Hyperlink","StatusBar","ToolBar","Tab","TabItem"]
    ; Pass 1: combined header "Price Items: N" in one node's Name or Value.
    ; Also remember the "Price Items:" label node for the split-header pass.
    lbl := ""
    for typeName in TYPES {
        elems := ""
        try elems := root.FindElements({Type: typeName})
        if (!elems)
            continue
        for el in elems {
            nm := ""
            vl := ""
            try nm := el.Name
            try vl := el.Value
            if (RegExMatch(nm, "i)Price\s*Items:?\s*(\d+)", &mm) || RegExMatch(vl, "i)Price\s*Items:?\s*(\d+)", &mm)) {
                LogMessage("    [counter] combined header -> " . mm[1])
                return mm[1]
            }
            if (nm = "Price Items:")
                lbl := el                       ; exact colon label preferred
            else if (lbl = "" && nm = "Price Items")
                lbl := el
        }
    }
    if (lbl = "")
        return ""

    ; Pass 2 (split header): the count is a separate node on the label's row,
    ; to its right. Spatial match uses only BoundingRectangle + Text scan (no
    ; Parent dependency). Pick the nearest pure-digit Text right of the label.
    lr := ""
    try lr := lbl.BoundingRectangle
    if (lr) {
        bestL := 999999
        best := ""
        for el in root.FindElements({Type: "Text"}) {
            en := ""
            try en := el.Name
            if (!RegExMatch(en, "^\s*(\d+)\s*$", &dm))
                continue
            er := ""
            try er := el.BoundingRectangle
            if (!er)
                continue
            if (er.t < lr.b && er.b > lr.t && er.l >= lr.l && er.l < bestL) {
                bestL := er.l
                best := dm[1]
            }
        }
        if (best != "") {
            LogMessage("    [counter] split header (spatial) -> " . best)
            return best
        }
    }

    ; Pass 2b (fallback): read the digit sibling under the label's parent.
    try {
        par := lbl.Parent
        if (par) {
            for k in par.GetChildren() {
                kn := ""
                try kn := k.Name
                if (kn = "")
                    try kn := k.Value
                if (RegExMatch(kn, "^\s*(\d+)\s*$", &km)) {
                    LogMessage("    [counter] split header (sibling) -> " . km[1])
                    return km[1]
                }
            }
        }
    }
    return ""
}

; ---------------------------------------------------------------------------
; True when Bravo is showing the Dashboard (presence of the dashboard-only
; intake controls "GM Intake" / "Jewelry Intake" / "Inventory Lookup", which
; don't exist in the Inventory working view). Uniquely named to avoid colliding
; with any shared lib helper.
; ---------------------------------------------------------------------------
IsOnDashboardITP() {
    try {
        root := GetBravoRoot()
        for typeName in ["Button", "Text", "TabItem"] {
            elems := ""
            try elems := root.FindElements({Type: typeName})
            if (!elems)
                continue
            for el in elems {
                n := ""
                try n := el.Name
                if (n = "")
                    continue
                if (n = "GM Intake" || n = "Jewelry Intake" || n = "Inventory Lookup")
                    return true
            }
        }
    } catch as e {
        LogMessage("    WARN IsOnDashboardITP: " . e.Message)
    }
    return false
}
