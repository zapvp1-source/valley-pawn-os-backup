; ============================================================================
; reports/ChekkitInactives.ahk
;
; Pulls the "Chekkit Inactives" saved Customer report (past 7 days), exports
; as CSV. This is the data feed for chekkit-weekly-review-requests Phase 1.
;
; SKILL it powers: chekkit-weekly-review-requests (Phase 1)
;
; UI path:
;   Dashboard -> Customers (sidebar)
;   -> right panel: Custom Reports
;   -> Bravo Custom Customer Report Generator dialog
;       -> Choose Saved Report dropdown -> "Chekkit Inactives" (SHARED COMPANY-WIDE)
;       -> Ok (uses saved criteria — past 7 days)
;   -> List view renders ("Customers - Specific: NN")
;   -> Export to CSV via Layouts -> Export... OR right-click -> Export.
;
; NOTE: Chekkit Inactives may not expose a standard Preview/Export... pattern
; like Reports module tiles do. Per the chained SKILL, manual transcription
; from the list view is the documented Phase 1 path. This module attempts the
; programmatic export first via the Layouts -> Export pattern; if that fails
; the diagnostic log dump will reveal what's actually available.
; ============================================================================

#Requires AutoHotkey v2.0

global CHEKKIT_ELEMENTS := Map(
    "sidebar_customers",    "Customers",
    "panel_custom_reports", "Custom Reports",
    "saved_report_combo",   "Choose Saved Report",
    "saved_report_value",   "Chekkit Inactives",
    "dialog_ok",            "Ok",
    "layouts_caret",        "Layouts",
    "panel_cancel",         "Cancel"
)

PullChekkitInactives(store, date, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "chekkit-inactives",
        "store",       store,
        "date",        date,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    outputPath := outputDir . "\" . OutputFilename(date, store, "chekkit-inactives")
    LogMessage("[" . store . "] ChekkitInactives date=" . date . " -> " . outputPath)

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

    try {
        DismissPopups()

        LogMessage("  step 1: open Customers")
        ClickByName(CHEKKIT_ELEMENTS["sidebar_customers"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: click Custom Reports in right panel")
        ClickByName(CHEKKIT_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(1500)

        LogMessage("  step 3: select 'Chekkit Inactives' from Choose Saved Report dropdown")
        SelectSavedReport(CHEKKIT_ELEMENTS["saved_report_combo"], CHEKKIT_ELEMENTS["saved_report_value"])

        LogMessage("  step 4: click Ok to run saved report")
        ClickByName(CHEKKIT_ELEMENTS["dialog_ok"], 5000)

        ; Wait for list to render. Heuristic: Layouts caret appears in the
        ; top-right of the list once data is loaded.
        if !FindByName(CHEKKIT_ELEMENTS["layouts_caret"], 30000)
            throw Error("Chekkit Inactives list did not render within 30s")
        ; DevExpress data grid takes 3-5s to populate rows after the layout
        ; renders. Underestimating this returns 0 rows even when data exists.
        Sleep(5000)

        ; Bravo's Customer list view does NOT expose Export under Layouts (only
        ; Saved Layouts / Delete Layout / Show summary panel are there). Walk
        ; the DevExpress data grid via UIA instead and write the CSV ourselves.
        LogMessage("  step 5: walk grid rows and write CSV")
        rowsWritten := WriteChekkitGridToCsv(outputPath)
        if (rowsWritten < 0) {
            LogVisibleNames()
            throw Error("Failed to walk Chekkit Inactives grid")
        }
        LogMessage("    wrote " . rowsWritten . " rows to CSV")
        result["row_count"] := rowsWritten

        ; Back to Dashboard
        try ClickByName(CHEKKIT_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        try ClickByName(CHEKKIT_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)

    } catch as e {
        LogVisibleNames()
        return Fail(result, started, "UIA click sequence failed: " . e.Message)
    }

    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: " . result["row_count"] . " rows, " . result["duration_ms"] . "ms")
    return result
}

; Walk the rendered DevExpress data grid in the Chekkit Inactives list view
; and write each row to a CSV with columns: first_name, last_name, phone,
; email, last_visit_date.
;
; Per the chekkit-3 diag dump: each cell in the grid is a Text element with
; AutoId=PART_Content. The list view header repeats column names ("Name",
; "Phone", "Address", "E-Mail", "Total Sales", "Total Buys", "Total Loans",
; "MobilePawn", "SMS"). Data cells have the actual customer values as their
; Name property.
;
; Strategy:
;   1. Find all Text elements with AutoId=PART_Content.
;   2. Get bounding rectangles and group cells by Y (same row).
;   3. Within each row, order cells by X.
;   4. Skip the header row (cells whose Name matches the known column labels).
;   5. Write the remaining rows to CSV.
;
; Returns row count, or -1 on failure.
WriteChekkitGridToCsv(outputPath) {
    rows := []
    try {
        root := GetBravoRoot()
        texts := root.FindElements({Type: "Text"})
        cells := []
        for t in texts {
            autoId := ""
            try autoId := t.AutomationId
            if (autoId != "PART_Content")
                continue
            n := ""
            try n := t.Name
            rect := 0
            try rect := t.BoundingRectangle
            if !rect
                continue
            yVal := 0
            xVal := 0
            try yVal := rect.t
            try xVal := rect.l
            cells.Push(Map("name", n, "x", xVal, "y", yVal))
        }
        if (cells.Length = 0)
            return -1

        ; Group cells by Y (within ±5 pixels of each other = same row)
        cellsSorted := SortCellsByYThenX(cells)
        currentRow := []
        currentY := -9999
        yTolerance := 8
        for c in cellsSorted {
            if (Abs(c["y"] - currentY) > yTolerance) {
                if (currentRow.Length > 0)
                    rows.Push(currentRow)
                currentRow := []
                currentY := c["y"]
            }
            currentRow.Push(c["name"])
        }
        if (currentRow.Length > 0)
            rows.Push(currentRow)
    } catch as e {
        LogMessage("    WARN WriteChekkitGridToCsv: " . e.Message)
        return -1
    }

    if (rows.Length = 0)
        return 0

    ; Identify the header row (one whose cells match known column labels)
    ; and skip it. Data rows follow.
    headerLabels := ["Name", "Phone", "Address", "E-Mail"]
    headerRowIdx := 0
    for idx, r in rows {
        match := 0
        for lbl in headerLabels {
            for cell in r {
                if (cell = lbl) {
                    match++
                    break
                }
            }
        }
        if (match >= 3) {
            headerRowIdx := idx
            break
        }
    }

    ; Write CSV
    FileAppend("first_name,last_name,phone,email,last_visit`r`n", outputPath, "UTF-8-RAW")
    count := 0
    for idx, r in rows {
        if (idx <= headerRowIdx)
            continue
        ; Heuristic: first cell is "First Last" or just "Name"; split on space
        name := r.Length >= 1 ? r[1] : ""
        firstName := ""
        lastName := ""
        if (name != "") {
            parts := StrSplit(name, " ", , 2)
            firstName := parts.Length >= 1 ? parts[1] : ""
            lastName := parts.Length >= 2 ? parts[2] : ""
        }
        phone := r.Length >= 2 ? r[2] : ""
        ; Address is in cell 3 — skip for now (downstream code only needs phone+email)
        email := r.Length >= 4 ? r[4] : ""
        ; Skip rows where name AND phone AND email are all empty
        if (firstName = "" && lastName = "" && phone = "" && email = "")
            continue
        WriteCsvRow(outputPath, firstName, lastName, phone, email, "")
        count++
    }
    return count
}

; Insertion sort cells by Y ascending, then X ascending.
SortCellsByYThenX(cells) {
    n := cells.Length
    if (n <= 1)
        return cells
    arr := cells.Clone()
    i := 2
    while (i <= n) {
        j := i
        while (j > 1) {
            a := arr[j]
            b := arr[j - 1]
            if (a["y"] < b["y"] || (a["y"] = b["y"] && a["x"] < b["x"])) {
                arr[j] := b
                arr[j - 1] := a
                j--
            } else {
                break
            }
        }
        i++
    }
    return arr
}

; Reusable helper for selecting an item from a "Choose Saved Report" combobox.
; Used by Chekkit Inactives, Loans 75-Day Past Due, FPD Cohort *, etc.
;
; Bravo's saved-report combo registers as UIA Type "Edit" with Name="BravoComboBox"
; (no AutoId). It is the BOTTOM-MOST BravoComboBox in the Custom Reports dialog —
; placed below all the criteria controls, right above the Ok/Cancel buttons.
; We find it by walking all "BravoComboBox" Edit elements and picking the one
; with the largest Y coordinate.
;
; Strategy:
;   1. Find the bottom-most BravoComboBox in the dialog.
;   2. Click it to open the dropdown.
;   3. ClickByName the desired saved-report row.
;   4. Fallback: keyboard navigation (focus, Down arrow, Enter).
SelectSavedReport(comboName, valueName) {
    combo := FindSavedReportCombo()
    if !combo {
        ; Last resort: try the named lookup (in case Bravo named it after all)
        combo := FindByName(comboName, 1500)
    }
    if !combo
        throw Error("SelectSavedReport: could not locate saved-report combo (looked for bottom-most BravoComboBox and Name='" . comboName . "')")
    try combo.Click("left")
    Sleep(700)
    try {
        ClickByName(valueName, 2500)
        LogMessage("    [saved-report] selected '" . valueName . "' by ClickByName")
        Sleep(300)
        return
    } catch as e {
        LogMessage("    WARN ClickByName '" . valueName . "' failed: " . e.Message)
    }
    ; Keyboard fallback: focus combo and arrow through the list.
    ; Without a known row index we can't pick deterministically — but we can
    ; try walking with a name compare. Send Down + check whether the combo's
    ; value matches valueName. Cap at 30 attempts (the saved-report list is
    ; rarely long).
    try combo.Focus()
    Sleep(200)
    Loop 30 {
        Send("{Down}")
        Sleep(150)
        try {
            cur := combo.Value
            if InStr(cur, valueName) {
                Send("{Enter}")
                Sleep(200)
                LogMessage("    [saved-report] selected '" . valueName . "' via keyboard walk after " . A_Index . " Down arrows")
                return
            }
        }
    }
    throw Error("SelectSavedReport: could not select '" . valueName . "' via click or keyboard walk")
}

; Find the saved-report combobox: the bottom-most BravoComboBox in the dialog.
; Returns 0 if none found.
FindSavedReportCombo() {
    bestElem := 0
    bestY := -1
    try {
        root := GetBravoRoot()
        ; The combo appears as UIA Edit type (Bravo's custom control)
        edits := root.FindElements({Type: "Edit"})
        for e in edits {
            n := ""
            try n := e.Name
            if (n != "BravoComboBox")
                continue
            ; Skip combos with an AutoId we know aren't the saved-report combo
            autoId := ""
            try autoId := e.AutomationId
            if (autoId = "BoxColumns" || autoId = "BoxIsShared" || autoId = "BoxSelectCriteria")
                continue
            ; Get bounding rect; pick the bottom-most
            rect := 0
            try rect := e.BoundingRectangle  ; {l, t, r, b}
            if !rect
                continue
            y := 0
            try y := rect.t
            if (y > bestY) {
                bestY := y
                bestElem := e
            }
        }
    } catch as e {
        LogMessage("    WARN FindSavedReportCombo: " . e.Message)
    }
    if bestElem
        LogMessage("    [saved-report] found bottom-most BravoComboBox at y=" . bestY)
    return bestElem
}
