; ============================================================================
; reports/PostToAccountingGL.ahk
;
; Exports the per-store Consolidated General Ledger from Bravo's
; "Post to Accounting" screen for a date range, as CSV.
;
; NEW FILE (additive, valley-pawn-context Rule #4). Cloned from
; reports/SalesAccounting.ahk (EndOfMonth family) — same range parsing,
; export-dialog helpers, result shape, robust exit.
;
; KEY DIFFERENCE from the EndOfMonth clones: navigation entry point is the
; Dashboard "Post to Accounting" button (Accounting section of the sidebar
; button strip), NOT the Reports module. Confirmed present in
; output/uia-tree-2026-07-03-dash.txt as [button] Name='Post to Accounting'.
;
; !! SAFETY — READ BEFORE EDITING !!
; The Post to Accounting screen exists to POST transactions to accounting —
; a state-changing action. This handler must NEVER click "Post", "Post All",
; "Post Selected", "Post to Accounting" (in-screen action button) or any
; similarly named commit control. It only: sets the date range, opens the
; "Consolidated Report" view, and exports the rendered report. Keep it that
; way.
;
; Trigger schema:
;   "name":   "post-to-accounting-gl"
;   "stores": ["CUL","HAR","LEX","ROA","WAY"]
;   "date":   "YYYY-MM-DD..YYYY-MM-DD"
;             or "discover[-<label>]" — DIAGNOSTIC mode: navigates into the
;             screen, dumps the UIA tree to output\uia-pta-<store>-*.txt at
;             each step, exits. Used to map element names; no export.
;
; Output filename: <END_DATE>_<STORE>_post-to-accounting-gl.csv
; ============================================================================
#Requires AutoHotkey v2.0

; Screen map (from output/uia-pta-CUL-20260706-132118.txt, Bravo 2026.6.0.79):
;   Top buttons: Done (btnDone) | More Records | Detail By Store |
;                Detail By Transaction | Consolidated General Ledger
;   "Export Format" label + BravoComboBox (export format dropdown)
;   itemsGrid: one row per unposted day, columns Posted(Post btn!)/Date/
;              Debits/Credits/Export. NEVER touch the Post buttons.
global PTAGL_ELEMENTS := Map(
    "dash_button",       "Post to Accounting",
    "view_consolidated", "Consolidated General Ledger",
    "preview_export",    "Export...",
    "export_ok",         "OK",
    "panel_done",        "Done",
    "panel_cancel",      "Cancel"
)

; ----------------------------------------------------------------------------
; ClampPtaGlEndDate(yyyymmdd) — same rule as EndOfMonth: Bravo date pickers
; refuse today/future dates; clamp to yesterday and log.
; ----------------------------------------------------------------------------
ClampPtaGlEndDate(yyyymmdd) {
    parts := StrSplit(yyyymmdd, "-")
    if (parts.Length != 3)
        return yyyymmdd
    reqStamp  := parts[1] . parts[2] . parts[3]
    todayStmp := FormatTime(A_Now, "yyyyMMdd")
    if (reqStamp < todayStmp)
        return yyyymmdd
    yest := DateAdd(A_Now, -1, "Days")
    return FormatTime(yest, "yyyy-MM-dd")
}

; Store combo item labels in the Consolidated GL dialog (match the CSV
; header "Store:" field, e.g. "LEX : VALLEY PAWN - LEXINGTON"). The combo
; DEFAULTS to "All stores" — selecting the specific store is mandatory or
; the export mixes all 5 stores.
PtaGlStoreItemName(store) {
    m := Map(
        "CUL", "CUL : VALLEY PAWN - CULPEPER",
        "HAR", "HAR : VALLEY PAWN - HARRISONBURG",
        "LEX", "LEX : VALLEY PAWN - LEXINGTON",
        "ROA", "ROA : VALLEY PAWN - ROANOKE",
        "WAY", "WAY : VALLEY PAWN - WAYNESBORO"
    )
    return m.Has(store) ? m[store] : store
}

; Select the target store in the dialog's Store BravoComboBox.
; Pattern mirrors NicsSelectFromCombo: expand the combo, then find the
; ListItem at the WINDOW ROOT (DevExpress popups live there, not under the
; combo). Exact name first, then prefix match on the store code.
; Read the combo's current text ("" if unreadable).
PtaGlComboValue(combo) {
    v := ""
    try v := combo.Value
    if (v = "") {
        try {
            inner := combo.FindElement({AutomationId: "PART_Editor"})
            if inner
                v := inner.Value
        }
    }
    return v
}

PtaGlSelectStore(combo, store, storeItem) {
    ; DevExpress combo commit is TREACHEROUS. Lessons (2026-07-06 + the
    ; IntakeDetail saved-report combo, same control family):
    ;   - SelectionItemPattern.Select() and UIA element .Click() both PAINT
    ;     the text (combo.Value reads the new store) WITHOUT committing the
    ;     bound value — the export still says "All stores".
    ;   - Keyboard (Alt+Down / type-search / Enter) does nothing at all.
    ;   - The ONLY committing gesture is a GENUINE mouse click at the item's
    ;     screen coordinates (MouseMove + Click), exactly like
    ;     IntakeSelectSavedReportCommitted().
    ; Findings so far (2026-07-06 tests 3-8):
    ;   - UIA item click / real item click at verified popup coords: paints
    ;     the text, does NOT commit (export still "All stores").
    ;   - Keyboard (arrows/type/Alt+Down): completely dead on this combo.
    ;   - A stray {Enter} submits the DIALOG (default Ok), not the combo.
    ;   - Neutral-label click after item click: still uncommitted (possible
    ;     DevExpress outside-click ROLLBACK if the popup was still open).
    ; THEORY (test 11): the combo's binding updates on LostFocus, and none
    ; of our gestures ever moved real WPF keyboard focus off the combo
    ; (UIA clicks on labels/text don't take focus). So: real-click the
    ; popup item, then REAL-CLICK INTO THE START DATE EDITOR — a genuinely
    ; focusable control — to force the blur commit. A committed selection
    ; survives the blur; an uncommitted paint reverts (which we can detect).
    CoordMode("Mouse", "Screen")
    ActivateBravo()
    Loop 2 {
        attempt := A_Index
        crect := 0
        try crect := combo.BoundingRectangle
        if !(crect && crect.r > crect.l) {
            LogMessage("    [store-combo] no usable combo rect")
            return false
        }
        ccx := (crect.l + crect.r) // 2
        ccy := (crect.t + crect.b) // 2
        MouseMove(ccx, ccy, 10)
        Sleep(150)
        Click(ccx, ccy)          ; REAL click: focus + open popup
        Sleep(900)
        LogMessage("    [store-combo] attempt " . attempt . " opened; value='" . PtaGlComboValue(combo) . "'")
        ; Real-click the popup item.
        el := 0
        try el := GetBravoRoot().FindElement({Type: "ListItem", Name: storeItem})
        if !el
            el := FindByName(storeItem, 1200)
        clicked := false
        if el {
            try el.ScrollIntoView()
            Sleep(300)
            r := 0
            try r := el.BoundingRectangle
            if (r && r.b > r.t && r.t > 0) {
                ecx := (r.l + r.r) // 2
                ecy := (r.t + r.b) // 2
                MouseMove(ecx, ecy, 10)
                Sleep(150)
                Click(ecx, ecy)
                Sleep(700)
                clicked := true
                LogMessage("    [store-combo] real-clicked item at " . ecx . "," . ecy)
            }
        }
        if !clicked {
            LogMessage("    [store-combo] item not clickable this attempt")
            Sleep(500)
            continue
        }
        ; Diagnostics: is the popup still open after the item click? An
        ; open popup means the click did not register as a selection, and
        ; any later outside click rolls the paint back.
        stillOpen := false
        try {
            li := GetBravoRoot().FindElement({Type: "ListItem", Name: storeItem})
            if li {
                off := true
                try off := li.IsOffscreen
                stillOpen := !off
            }
        }
        val := PtaGlComboValue(combo)
        LogMessage("    [store-combo] after item click: value='" . val . "' popup-still-open=" . (stillOpen ? "yes" : "no"))
        if InStr(val, store)
            return true
        Sleep(500)
    }
    ; Combo never confirmed. The CSV header check (step 9c) is the final
    ; gate, so return false and let the caller fail loudly.
    return false
}

; Real-mouse click on the dialog's Ok (its clickable element is the 'Ok'
; text child of a nameless button — a REAL click also moves WPF focus,
; which UIA text-clicks do not).
PtaGlRealClickOk() {
    CoordMode("Mouse", "Screen")
    el := 0
    try el := FindByName("Ok", 2000)
    if !el
        return false
    r := 0
    try r := el.BoundingRectangle
    if !(r && r.r > r.l)
        return false
    MouseMove((r.l + r.r) // 2, (r.t + r.b) // 2, 10)
    Sleep(120)
    Click((r.l + r.r) // 2, (r.t + r.b) // 2)
    LogMessage("    [ok] real-clicked Ok at " . ((r.l + r.r) // 2) . "," . ((r.t + r.b) // 2))
    return true
}

; Dump the current Bravo UIA tree into a discovery file with a section header.
; Reuses DumpUiaTree() from reports/UIADiscover.ahk (same include namespace).
PtaGlDump(outputPath, label) {
    section := "`r`n=========================================`r`n"
    section .= "PTA-GL discover [" . label . "]  " . FormatTime(, "yyyy-MM-dd HH:mm:ss") . "`r`n"
    try section .= "Title: " . WinGetTitle("A") . "`r`n"
    section .= "=========================================`r`n"
    try {
        root := GetBravoRoot()
        section .= DumpUiaTree(root, 0, 12)
    } catch as e {
        section .= "ERROR walking tree: " . e.Message . "`r`n"
    }
    FileAppend(section, outputPath, "UTF-8")
    LogMessage("    [discover] dumped section '" . label . "' -> " . outputPath)
}

; Best-effort exit from the Post to Accounting screen back to Dashboard.
; Order: named Cancel, Done, Escape, then BackToDashboard safety net.
; NEVER clicks anything containing "Post".
PtaGlExitToDashboard() {
    try ActivateBravo()
    Sleep(400)
    Loop 3 {
        onDash := false
        try onDash := ExistsByName("Reports")
        if onDash
            break
        exited := false
        try {
            ClickByName(PTAGL_ELEMENTS["panel_cancel"], 1500)
            exited := true
        }
        if !exited {
            try {
                ClickByName(PTAGL_ELEMENTS["panel_done"], 1500)
                exited := true
            }
        }
        if !exited
            Send("{Escape}")
        Sleep(1200)
        try DismissPopups()
    }
    onDash := false
    try onDash := ExistsByName("Reports")
    if !onDash {
        LogMessage("    [exit] BackToDashboard safety net")
        try BackToDashboard(8)
    }
    Sleep(400)
    try DismissPopups()
}

PullPostToAccountingGL(store, dateOrRange, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "post-to-accounting-gl",
        "store",       store,
        "date",        dateOrRange,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    ; --- Discover (diagnostic) mode -----------------------------------------
    isDiscover := InStr(dateOrRange, "discover")

    ; --- Parse date range ----------------------------------------------------
    startDateIso := ""
    endDateIso := ""
    if !isDiscover {
        if InStr(dateOrRange, "..") {
            parts := StrSplit(dateOrRange, "..")
            if (parts.Length != 2)
                return Fail(result, started, "Malformed date range: " . dateOrRange . " (expected YYYY-MM-DD..YYYY-MM-DD)")
            startDateIso := Trim(parts[1])
            endDateIso := Trim(parts[2])
        } else {
            startDateIso := dateOrRange
            endDateIso := dateOrRange
        }
        origEndDateIso := endDateIso
        endDateIso := ClampPtaGlEndDate(endDateIso)
        if (endDateIso != origEndDateIso)
            LogMessage("[" . store . "] PostToAccountingGL end date clamped: " . origEndDateIso . " -> " . endDateIso . " (Bravo rejects today/future)")
        LogMessage("[" . store . "] PostToAccountingGL range=" . startDateIso . ".." . endDateIso)
    } else {
        LogMessage("[" . store . "] PostToAccountingGL DISCOVER mode (" . dateOrRange . ")")
    }

    outputPath := isDiscover
        ? outputDir . "\uia-pta-" . store . "-" . FormatTime(, "yyyyMMdd-HHmmss") . ".txt"
        : outputDir . "\" . OutputFilename(endDateIso, store, "post-to-accounting-gl")
    LogMessage("  output -> " . outputPath)

    if !WaitForBravoReady(30)
        return Fail(result, started, "Bravo window not found/ready within 30s")
    ActivateBravo()
    DismissPopups()

    global CONFIG
    password := CONFIG.Has("bravo.password") ? CONFIG["bravo.password"] : ""
    if !EnsureStore(store, password)
        return Fail(result, started, "EnsureStore failed for " . store)
    LogMessage("  store confirmed: " . store)

    if !isDiscover
        ResetOutputFile(outputPath)

    if !BackToDashboard()
        return Fail(result, started, "BackToDashboard could not return Bravo to Dashboard")
    Sleep(500)
    DismissPopups()

    try {
        DismissPopups()

        LogMessage("  step 1: click Dashboard 'Post to Accounting' button")
        ClickByName(PTAGL_ELEMENTS["dash_button"], 8000)
        Sleep(3500)
        DismissPopups()

        if isDiscover {
            PtaGlDump(outputPath, "after-open-post-to-accounting")

            ; Open the Consolidated General Ledger dialog and dump it.
            ; Dialog (mapped 2026-07-06): "Reporting Dates" + 2x BravoDateEdit,
            ; "Store" + BravoComboBox, Ok (empty Name, text child 'Ok'), Cancel.
            if ExistsByName(PTAGL_ELEMENTS["view_consolidated"]) {
                LogMessage("  [discover] clicking 'Consolidated General Ledger'")
                try {
                    ClickByName(PTAGL_ELEMENTS["view_consolidated"], 3000)
                    Sleep(4000)
                    PtaGlDump(outputPath, "after-consolidated-general-ledger")
                    if InStr(dateOrRange, "6") {
                        ; June-popup discover: submit a JUNE range and dump
                        ; the tree BEFORE dismissing whatever popup appears
                        ; (June cells all failed with a btnOk popup after Ok).
                        try SetReportDate(1, "2026-06-01")
                        Sleep(400)
                        try SetReportDate(2, "2026-06-30")
                        Sleep(600)
                        ; Full normal sequence incl. store select (the June
                        ; popup only fired on the full flow).
                        combo := 0
                        try {
                            dlg := GetBravoRoot().FindElement({Type: "Window"})
                            if dlg
                                combo := dlg.FindElement({Name: "BravoComboBox"})
                        }
                        if combo
                            PtaGlSelectStore(combo, store, PtaGlStoreItemName(store))
                        LogMessage("  [discover-6] real-click Ok for June range")
                        PtaGlRealClickOk()
                        Sleep(2500)
                        PtaGlDump(outputPath, "after-ok-june-popup-undismissed")
                        section := "`r`n----- DESKTOP ROOT after June Ok (rects) -----`r`n"
                        try {
                            desktop := UIA.GetRootElement()
                            section .= DumpUiaTreeRects(desktop, 0, 8)
                        } catch as e6 {
                            section .= "ERROR: " . e6.Message . "`r`n"
                        }
                        FileAppend(section, outputPath, "UTF-8")
                        try DismissPopups()
                        Sleep(2000)
                        PtaGlDump(outputPath, "after-popup-dismissed")
                        Send("{Escape}")
                        Sleep(1000)
                        try ClickByName("Cancel", 2000)
                        Sleep(800)
                        try DismissPopups()
                    } else if InStr(dateOrRange, "5") {
                        ; Visual-verify discover: run the REAL selection +
                        ; dates, then HOLD the dialog open 45s so an external
                        ; screenshot can show what the human-visible dialog
                        ; says (CUL vs All stores) before any Ok.
                        combo := 0
                        try {
                            dlg := GetBravoRoot().FindElement({Type: "Window"})
                            if dlg
                                combo := dlg.FindElement({Name: "BravoComboBox"})
                        }
                        if combo {
                            PtaGlSelectStore(combo, store, PtaGlStoreItemName(store))
                            try SetReportDate(1, "2026-04-01")
                            Sleep(400)
                            try SetReportDate(2, "2026-04-30")
                            Sleep(600)
                            LogMessage("  [discover-5] HOLDING dialog open 45s for screenshot; combo value='" . PtaGlComboValue(combo) . "'")
                            Sleep(45000)
                            LogMessage("  [discover-5] hold done; combo value='" . PtaGlComboValue(combo) . "'")
                        } else {
                            LogMessage("  [discover-5] combo not found")
                        }
                        try ClickByName("Cancel", 3000)
                        Sleep(1000)
                        try DismissPopups()
                    } else if InStr(dateOrRange, "4") {
                        ; Popup-geometry discover: open the Store combo popup
                        ; via a REAL click on its PART_Item (v) button, dump
                        ; rects everywhere, then HOLD it open 30s so an
                        ; external _session1_shot.ps1 can photograph it.
                        CoordMode("Mouse", "Screen")
                        combo := 0
                        try {
                            dlg := GetBravoRoot().FindElement({Type: "Window"})
                            if dlg
                                combo := dlg.FindElement({Name: "BravoComboBox"})
                        }
                        if combo {
                            cr := 0
                            try cr := combo.BoundingRectangle
                            if cr
                                LogMessage("  [discover-4] combo rect=[" . cr.l . "," . cr.t . "," . cr.r . "," . cr.b . "]")
                            btn := 0
                            try btn := combo.FindElement({AutomationId: "PART_Item"})
                            br := 0
                            if btn {
                                try br := btn.BoundingRectangle
                                if br
                                    LogMessage("  [discover-4] PART_Item rect=[" . br.l . "," . br.t . "," . br.r . "," . br.b . "]")
                            }
                            if (br && br.r > br.l) {
                                MouseMove((br.l + br.r) // 2, (br.t + br.b) // 2, 10)
                                Sleep(150)
                                Click((br.l + br.r) // 2, (br.t + br.b) // 2)
                                LogMessage("  [discover-4] real-clicked PART_Item")
                            } else if (cr && cr.r > cr.l) {
                                MouseMove((cr.l + cr.r) // 2, (cr.t + cr.b) // 2, 10)
                                Sleep(150)
                                Click((cr.l + cr.r) // 2, (cr.t + cr.b) // 2)
                                LogMessage("  [discover-4] real-clicked combo center (no PART_Item rect)")
                            }
                            Sleep(2000)
                            ; Where do the item elements claim to be?
                            for srcName, srcRoot in Map("bravo-root", GetBravoRoot(), "desktop-root", UIA.GetRootElement()) {
                                try {
                                    lis := srcRoot.FindElements({Type: "ListItem"})
                                    n := 0
                                    for li in lis {
                                        ln := ""
                                        try ln := li.Name
                                        if !InStr(ln, "VALLEY PAWN") && ln != "All stores"
                                            continue
                                        lr := 0
                                        try lr := li.BoundingRectangle
                                        rs := lr ? ("[" . lr.l . "," . lr.t . "," . lr.r . "," . lr.b . "]") : "none"
                                        off := ""
                                        try off := li.IsOffscreen ? " OFFSCREEN" : ""
                                        LogMessage("  [discover-4] " . srcName . " item '" . ln . "' rect=" . rs . off)
                                        n += 1
                                    }
                                    LogMessage("  [discover-4] " . srcName . ": " . n . " store items")
                                } catch as e4 {
                                    LogMessage("  [discover-4] " . srcName . " scan error: " . e4.Message)
                                }
                            }
                            PtaGlDump(outputPath, "popup-open-bravo-tree")
                            LogMessage("  [discover-4] HOLDING popup open 30s for screenshot")
                            Sleep(30000)
                            Send("{Escape}")
                            Sleep(800)
                        } else {
                            LogMessage("  [discover-4] combo not found")
                        }
                        ; Leave the dialog via Cancel.
                        try ClickByName("Cancel", 3000)
                        Sleep(1000)
                        try DismissPopups()
                    } else if InStr(dateOrRange, "3") {
                        ; Deep discover: set an April range, submit Ok, and
                        ; dump whatever renders (preview vs save dialog).
                        LogMessage("  [discover-3] set dates 2026-04-01..2026-04-30")
                        try SetReportDate(1, "2026-04-01")
                        Sleep(500)
                        try SetReportDate(2, "2026-04-30")
                        Sleep(800)
                        LogMessage("  [discover-3] click Ok")
                        ClickByName("Ok", 5000)
                        Sleep(8000)
                        try DismissPopups()
                        PtaGlDump(outputPath, "after-consolidated-ok")
                        section := "`r`n----- DESKTOP ROOT (popups, with rects) -----`r`n"
                        try {
                            desktop := UIA.GetRootElement()
                            section .= DumpUiaTreeRects(desktop, 0, 9)
                        } catch as e2 {
                            section .= "ERROR walking desktop root: " . e2.Message . "`r`n"
                        }
                        FileAppend(section, outputPath, "UTF-8")
                        ; Close whatever opened without exporting.
                        Send("{Escape}")
                        Sleep(1200)
                        Send("{Escape}")
                        Sleep(1200)
                        try DismissPopups()
                    } else {
                        ; Shallow discover: close the dialog without running it.
                        Send("{Escape}")
                        Sleep(1200)
                        try DismissPopups()
                    }
                } catch as e {
                    LogMessage("  [discover] consolidated flow failed: " . e.Message)
                    try Send("{Escape}")
                    Sleep(800)
                }
            } else {
                LogMessage("  [discover] no 'Consolidated General Ledger' element on this screen")
            }

            PtaGlExitToDashboard()
            result["output_path"] := outputPath
            result["row_count"]   := 1
            result["status"]      := "success"
            result["duration_ms"] := A_TickCount - started
            LogMessage("  DISCOVER SUCCESS: " . result["duration_ms"] . "ms")
            return result
        }

        ; --- Normal mode ------------------------------------------------
        ; step 2: open the Consolidated General Ledger dialog.
        LogMessage("  step 2: click 'Consolidated General Ledger'")
        ClickByName(PTAGL_ELEMENTS["view_consolidated"], 8000)
        Sleep(2500)
        DismissPopups()
        ; The dialog has "Reporting Dates" + two BravoDateEdit fields, a
        ; Store combo (defaults to current store), Ok and Cancel.
        if !FindByName("Reporting Dates", 10000)
            throw Error("Consolidated General Ledger dialog did not appear within 10s")

        ; step 3: set the date range FIRST (1=Start, 2=End, left-to-right).
        ; Order matters: any dialog interaction AFTER the store selection
        ; rolls the combo back to "All stores" (observed in discover-5),
        ; so dates go first and the store pick is the LAST gesture before Ok.
        LogMessage("  step 3a: SetReportDate(1, " . startDateIso . ")")
        SetReportDate(1, startDateIso)
        Sleep(500)
        LogMessage("  step 3b: SetReportDate(2, " . endDateIso . ")")
        SetReportDate(2, endDateIso)
        Sleep(800)

        ; step 3c: select THIS store in the dialog's Store combo (defaults
        ; to "All stores" which exports a mixed-store GL — never ship that).
        storeItem := PtaGlStoreItemName(store)
        LogMessage("  step 3c: select store '" . storeItem . "'")
        combo := 0
        try {
            dlg := GetBravoRoot().FindElement({Type: "Window"})
            if dlg
                combo := dlg.FindElement({Name: "BravoComboBox"})
        }
        if !combo {
            ; Fallback: the dialog renders before the main screen in document
            ; order, so the first BravoComboBox at root is the Store combo.
            try combo := GetBravoRoot().FindElement({Name: "BravoComboBox"})
        }
        if !combo
            throw Error("Store combo (BravoComboBox) not found in Consolidated GL dialog")
        if !PtaGlSelectStore(combo, store, storeItem)
            throw Error("Could not select store '" . storeItem . "' in Store combo")

        ; step 4: submit IMMEDIATELY — real-click Ok as the very next
        ; gesture after the store pick (any other interaction rolls the
        ; combo back to "All stores"). Verify the dialog closed and retry.
        LogMessage("  step 4: click Ok (immediate, verified close)")
        okClosed := false
        Loop 4 {
            if !PtaGlRealClickOk() {
                try ClickByName("Ok", 5000)
            }
            Sleep(2500)
            if !ExistsByName("Reporting Dates") {
                okClosed := true
                LogMessage("    [ok] dialog closed after attempt " . A_Index)
                break
            }
            LogMessage("    [ok] dialog still open after attempt " . A_Index . " — nudging focus and retrying")
            ActivateBravo()
            Send("{Tab}")
            Sleep(600)
            if (A_Index = 2) {
                Send("{Enter}")
                Sleep(1500)
                if !ExistsByName("Reporting Dates") {
                    okClosed := true
                    LogMessage("    [ok] dialog closed via Enter")
                    break
                }
            }
        }
        if !okClosed
            throw Error("Consolidated GL dialog did not close after Ok attempts")
        Sleep(1000)
        DismissPopups()

        ; step 5: wait for the DevExpress preview's Export... ribbon item.
        if !FindByName(PTAGL_ELEMENTS["preview_export"], 60000)
            throw Error("Consolidated GL preview did not render within 60s (Export... never appeared)")
        Sleep(800)

        LogMessage("  step 5: click Export...")
        ClickByName(PTAGL_ELEMENTS["preview_export"], 5000)
        if !FindByName(PTAGL_ELEMENTS["export_ok"], 8000)
            throw Error("Export Document dialog did not appear within 8s")
        Sleep(800)

        LogMessage("  step 6: set Export format = Csv")
        SetExportFormatCsv()

        LogMessage("  step 7: set File path = " . outputPath)
        SetExportFilePath(outputPath)

        LogMessage("  step 8: uncheck open-after-export")
        UncheckOpenAfterExport()

        LogMessage("  step 9: click export OK")
        ClickByName(PTAGL_ELEMENTS["export_ok"], 5000)

        if !WaitForFile(outputPath, 180)
            throw Error("CSV file did not appear at " . outputPath . " within 180s")
        Sleep(2000)

        ; Reject empty/partial exports. A real Consolidated GL CSV is ~4 KB.
        sz := 0
        try sz := FileGetSize(outputPath)
        if (sz < 300) {
            throw Error("Exported CSV is too small (" . sz . " bytes) — export likely failed mid-write. Path: " . outputPath)
        }
        LogMessage("  step 9b: CSV size check passed (" . sz . " bytes)")

        ; step 9c: verify the export is store-specific. The header spans the
        ; first ~3 physical lines; line 3 is ",Store:,,<CODE> : VALLEY PAWN -
        ; <CITY>" (or "All stores" when the combo selection silently failed —
        ; reject that).
        hdr := ""
        try {
            f := FileOpen(outputPath, "r")
            Loop 5 {
                if f.AtEOF
                    break
                hdr .= f.ReadLine() . " | "
            }
            f.Close()
        }
        if InStr(hdr, "All stores") || !InStr(hdr, store . " :") {
            throw Error("Exported GL is not store-specific for " . store . " (header: " . SubStr(hdr, 1, 200) . ")")
        }
        LogMessage("  step 9c: store header check passed (" . store . ")")

        ; step 10: exit back to Dashboard (Cancel-first, never Post).
        LogMessage("  step 10: exit to Dashboard")
        PtaGlExitToDashboard()

    } catch as e {
        ; Cascade-safe recovery: never leave Bravo stranded on this screen.
        try {
            LogMessage("    [recovery] best-effort exit to Dashboard")
            PtaGlExitToDashboard()
        }
        return Fail(result, started, "UIA click sequence failed: " . e.Message)
    }

    rowCount := CountCsvRows(outputPath)
    result["row_count"]   := rowCount
    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: " . rowCount . " rows, " . result["duration_ms"] . "ms")
    return result
}
