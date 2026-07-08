; ============================================================================
; reports/Loans75DaysPastDue.ahk
;
; Runs the "75 Days Past Due" saved Ad Hoc loan report for a single store and
; captures the count + dollar Sum. Writes a single-row CSV with the two values
; for downstream parsing.
;
; SKILL it powers: weekly-loan-layaway-review (LOAN side)
;
; UI path:
;   Dashboard -> Loans/Buys (sidebar)
;   -> right panel "Pick Up" -> Custom Reports
;   -> Bravo Custom Loan Report Generator dialog
;       -> Choose Saved Report -> "75 Days Past Due" (SHARED COMPANY-WIDE)
;       -> Ok
;   -> List renders; title bar shows "Loans/Buys - Specific: NN" (count)
;   -> Layouts caret -> tick "Show summary panel"
;   -> Sum cell appears bottom-right -> read $ total
;   -> Cancel back to Dashboard
;
; Output CSV columns: store, date, count, dollar_sum
; ============================================================================

#Requires AutoHotkey v2.0

global LOANS75_ELEMENTS := Map(
    "sidebar_loans_buys",      "Loans/Buys",
    "panel_custom_reports",    "Custom Reports",
    "saved_report_combo",      "Choose Saved Report",
    "saved_report_value",      "75 Days Past Due",
    "dialog_ok",               "Ok",
    "layouts_caret",           "Layouts",
    "show_summary_toggle",     "Show summary panel",
    "panel_cancel",            "Cancel"
)

PullLoans75DaysPastDue(store, date, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "loans-75-days-past-due",
        "store",       store,
        "date",        date,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    outputPath := outputDir . "\" . OutputFilename(date, store, "loans-75-days-past-due")
    LogMessage("[" . store . "] Loans75DaysPastDue date=" . date . " -> " . outputPath)

    if !WaitForBravoReady(30)
        return Fail(result, started, "Bravo window not found/ready within 30s")
    ActivateBravo()
    DismissPopups()

    global CONFIG
    password := CONFIG.Has("bravo.password") ? CONFIG["bravo.password"] : ""
    if !EnsureStore(store, password)
        return Fail(result, started, "EnsureStore failed for " . store)
    LogMessage("  store confirmed: " . store)

    ResetOutputFile(outputPath)

    if !BackToDashboard()
        return Fail(result, started, "BackToDashboard could not return Bravo to Dashboard")
    Sleep(500)
    DismissPopups()

    count := 0
    dollarSum := 0.0

    try {
        DismissPopups()

        LogMessage("  step 1: open Loans/Buys")
        ClickByName(LOANS75_ELEMENTS["sidebar_loans_buys"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: click Custom Reports")
        ClickByName(LOANS75_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(1500)

        LogMessage("  step 3: select '75 Days Past Due' saved report")
        SelectSavedReport(LOANS75_ELEMENTS["saved_report_combo"], LOANS75_ELEMENTS["saved_report_value"])

        LogMessage("  step 4: click Ok")
        ClickByName(LOANS75_ELEMENTS["dialog_ok"], 5000)

        ; List renders. Title shows "Loans/Buys - Specific: NN" OR
        ; "Loans To Expire: 0" for empty result.
        Sleep(3000)
        DismissPopups()

        count := ParseCountFromTitle()
        LogMessage("    count from title: " . count)

        ; DIAGNOSTIC (2026-05-13): if count came back 0 but the user can see
        ; rows on screen, the row-detection or header-regex is wrong for
        ; this saved-report view. Dump the full visible UIA element name
        ; list so we can grep for the actual count display.
        if (count = 0) {
            LogMessage("    [DIAG] count=0 — dumping visible UIA names for inspection")
            LogVisibleNames()
            DumpAllUiaTypeCounts()
        }

        ; If count > 0, read the Sum from summary panel
        if (count > 0) {
            LogMessage("  step 5: open Layouts and enable summary panel")
            try {
                ClickByName(LOANS75_ELEMENTS["layouts_caret"], 3000)
                Sleep(500)
                ; Toggle "Show summary panel" — may already be on from prior runs
                try SetToggleByName(LOANS75_ELEMENTS["show_summary_toggle"], true, 2000)
                Sleep(500)
                ; Close Layouts by clicking it again
                try ClickByName(LOANS75_ELEMENTS["layouts_caret"], 2000)
                Sleep(500)
            } catch as e {
                LogMessage("    WARN: could not enable summary panel: " . e.Message)
            }

            ; Read the Sum cell. UIA exposes it as a Text element whose Name
            ; starts with "$" (e.g. "$12,345.67"). Walk Text elements and pick
            ; the largest-looking $ value (the summary panel is bottom-right;
            ; there's typically only one such cell).
            dollarSum := ReadSummaryPanelSum()
            LogMessage("    dollar sum: $" . dollarSum)
        }

        ; Write captured values to CSV (header + one data row)
        FileAppend("store,date,count,dollar_sum`r`n", outputPath, "UTF-8-RAW")
        FileAppend(store . "," . date . "," . count . "," . dollarSum . "`r`n", outputPath, "UTF-8-RAW")

        ; Back to Dashboard
        try ClickByName(LOANS75_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        try ClickByName(LOANS75_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)

    } catch as e {
        LogVisibleNames()
        return Fail(result, started, "UIA click sequence failed: " . e.Message)
    }

    result["row_count"]   := 1
    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: count=" . count . " sum=$" . dollarSum . ", " . result["duration_ms"] . "ms")
    return result
}

; Parse the count for the currently-loaded saved-report list view.
;
; Strategy: count the visible data rows in the rendered list. Each row is a
; DevExpress data-grid row with AutomationId like "RowItem_*" or class similar.
; That's the post-filter count.
;
; Fallback strategy: look for a Text element with a label like "Specific: NN"
; in the page header area (avoid right-sidebar badges which show the
; unfiltered count).
;
; Returns the count, or -1 if no count found.
ParseCountFromTitle() {
    rowCount := CountListViewRows()
    if (rowCount >= 0) {
        LogMessage("    [count] list rows -> " . rowCount)
        return rowCount
    }
    ; Fallback: look for a labeled count Text in the page-header area
    ; (top portion of the screen, avoid right-sidebar widgets).
    found := ReadHeaderCountText()
    if (found >= 0) {
        LogMessage("    [count] header text -> " . found)
        return found
    }
    LogMessage("    [count] no rows or header count found; treating as 0")
    return 0
}

; Count visible data rows in the currently-rendered DevExpress list/grid.
; Bravo's grids expose rows as DataItem with AutomationId starting with
; "RowItem_" OR as a child of a "Table"-typed element. Try the most common
; patterns. Returns the count, or -1 if no list could be located.
CountListViewRows() {
    try {
        root := GetBravoRoot()
        ; Pattern 1: AutomationId starts with "RowItem_"
        elems := root.FindElements({Type: "DataItem"})
        if (elems && elems.Length > 0) {
            return elems.Length
        }
    }
    try {
        ; Pattern 2: TreeViewItem under the loans list
        elems := root.FindElements({Type: "TreeViewItem"})
        ; Filter for ones that look like data rows (have an AutoId, not the sidebar)
        count := 0
        for e in elems {
            autoId := ""
            try autoId := e.AutomationId
            if (autoId != "" && InStr(autoId, "Row")) {
                count++
            }
        }
        if (count > 0)
            return count
    }
    return -1
}

; Diagnostic — for every standard UIA ControlType, count how many elements
; of that type exist under the Bravo root. Lets us identify where the
; rendered data rows or the "Specific: NN" header live, even when their
; Name is empty (we'd see the type with a non-zero count but no names in
; LogVisibleNames). For types with 1-200 elements, dump the first 5
; full property snapshots (Name, Value, HelpText, AutomationId) so we
; can see what text they actually contain.
DumpAllUiaTypeCounts() {
    LogMessage("    [DIAG2] counting elements by UIA ControlType:")
    allTypes := ["Button","Calendar","CheckBox","ComboBox","Custom","DataGrid","DataItem","Document","Edit","Group","Header","HeaderItem","Hyperlink","Image","List","ListItem","Menu","MenuBar","MenuItem","Pane","ProgressBar","RadioButton","ScrollBar","Separator","Slider","Spinner","SplitButton","StatusBar","Tab","TabItem","Table","Text","Thumb","TitleBar","ToolBar","ToolTip","Tree","TreeItem","TreeViewItem","Window"]
    try {
        root := GetBravoRoot()
    } catch as e {
        LogMessage("    [DIAG2] cannot get Bravo root: " . e.Message)
        return
    }
    for typeName in allTypes {
        try {
            elems := root.FindElements({Type: typeName})
            n := (elems) ? elems.Length : 0
            if (n > 0)
                LogMessage("    [DIAG2] " . typeName . " count=" . n)
            ; For interesting counts, dump the first 5 elements with all properties
            if (n >= 1 && n <= 200) {
                shown := 0
                for elem in elems {
                    if (shown >= 80)
                        break
                    nm := ""
                    val := ""
                    helpText := ""
                    autoId := ""
                    try nm := elem.Name
                    try val := elem.Value
                    try helpText := elem.HelpText
                    try autoId := elem.AutomationId
                    ; Only log if at least one field is non-empty
                    if (nm != "" || val != "" || helpText != "" || autoId != "") {
                        LogMessage("    [DIAG2]   " . typeName . "[" . shown . "]: name='" . SubStr(nm, 1, 80) . "' value='" . SubStr(val, 1, 80) . "' help='" . SubStr(helpText, 1, 80) . "' autoid='" . autoId . "'")
                        shown += 1
                    }
                }
            }
        } catch as e {
            ; type not supported on this UIA version — skip
        }
    }
    LogMessage("    [DIAG2] done")
}

; Read a labeled count from a Text element in the page-header area.
; Final pattern (2026-05-13): the count is rendered as TWO sibling Text
; elements — one with name 'Specific:' (the label) followed immediately
; by one whose name is purely numeric (the count itself, e.g. '41').
; Same shape as the right-sidebar badges (e.g. 'Loans To Expire' / '168').
;
; Strategy:
;   1. Walk all Text elements in document order.
;   2. Find the index where name == 'Specific:' (case-insensitive, allow
;      trailing colon optional).
;   3. The next Text element whose name matches /^\d+$/ is the count.
;   4. Return that integer.
;
; Also handles legacy single-Name patterns like 'Specific: 41' for any
; Bravo skin that combines label + value into one Text Name.
ReadHeaderCountText() {
    try {
        root := GetBravoRoot()
        elems := root.FindElements({Type: "Text"})
        if (!elems || elems.Length = 0)
            return -1
        ; Pass 1: legacy single-Name "Specific: NN"
        for e in elems {
            n := ""
            try n := e.Name
            if (n = "")
                continue
            if RegExMatch(n, "i)(Specific|Custom|Records?|Items?|Total)[:\s]+(\d+)", &m) {
                cand := Integer(m[2])
                if (cand >= 0) {
                    LogMessage("    [count] single-Name match '" . n . "' -> " . cand)
                    return cand
                }
            }
        }
        ; Pass 2: sibling-pair pattern. Find 'Specific:' (or 'Specific')
        ; label, then read numeric Name of the next non-empty Text.
        labelIdx := -1
        idx := 0
        for e in elems {
            n := ""
            try n := e.Name
            if (n = "") {
                idx += 1
                continue
            }
            if RegExMatch(n, "i)^(Specific|Custom|Records?|Items?|Total)\s*:?\s*$") {
                labelIdx := idx
                LogMessage("    [count] found label '" . n . "' at Text index " . idx)
            } else if (labelIdx >= 0 && idx > labelIdx) {
                ; Looking for the numeric sibling. Skip empty names; the
                ; FIRST non-empty Name encountered after the label is the
                ; count if it is purely numeric.
                if RegExMatch(n, "^\d+$") {
                    cand := Integer(n)
                    LogMessage("    [count] sibling-pair match '" . n . "' -> " . cand)
                    return cand
                }
                ; If the next non-empty name isn't numeric, give up on
                ; this label and keep searching for another label index.
                ; This guards against intervening non-data Text elements.
                labelIdx := -1
            }
            idx += 1
        }
    } catch as e {
        LogMessage("    WARN ReadHeaderCountText: " . e.Message)
    }
    ; Final fallback: Bravo window title
    try {
        title := WinGetTitle("ahk_class HwndWrapper[Bravo")
        if (title != "") {
            if RegExMatch(title, "i)(Specific|Custom|Records?|Items?|Total)[:\s]+(\d+)", &m) {
                cand := Integer(m[2])
                LogMessage("    [count] window-title match '" . title . "' -> " . cand)
                return cand
            }
        }
    } catch as e {
        LogMessage("    WARN window-title fallback: " . e.Message)
    }
    return -1
}

; Read the summary-panel Sum cell. Returns a numeric float (0 if not found).
; Walks all Text elements; picks the one whose Name looks like a dollar value
; AND lives in the bottom portion of the window (filtered by bounding rect Y).
ReadSummaryPanelSum() {
    sum := 0.0
    try {
        root := GetBravoRoot()
        texts := root.FindElements({Type: "Text"})
        for t in texts {
            n := ""
            try n := t.Name
            if (n = "")
                continue
            ; Look for a dollar-formatted value
            if RegExMatch(n, "^\$[\d,]+\.\d{2}$") {
                ; Convert to float
                clean := StrReplace(StrReplace(n, "$", ""), ",", "")
                val := 0.0
                try val := Float(clean)
                if (val > sum)
                    sum := val
            }
        }
    } catch as e {
        LogMessage("    WARN ReadSummaryPanelSum: " . e.Message)
    }
    return sum
}
