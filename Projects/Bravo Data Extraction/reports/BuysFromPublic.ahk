; ============================================================================
; reports/BuysFromPublic.ahk
;
; Runs the "Buys From Public — Master" saved Ad Hoc Loan/Buy report for a
; single store across a configurable date range, exports the full row detail
; as CSV. Powers the Deep KPI Analysis project (cumulative + weekly buys
; reviews).
;
; SKILL it powers: deep-kpi-buys (Excel KPI workbook + scheduled reviews)
;
; UI path:
;   Dashboard -> Loans/Buys (sidebar)
;   -> right panel "Pick Up" -> Custom Reports
;   -> Bravo Custom Loan Report Generator dialog
;       -> Choose Saved Report -> "Buys From Public — Master" (SHARED COMPANY-WIDE)
;       -> [saved filters load — Transaction Type=Buy, plus a Transaction Date
;          between-range placeholder]
;       -> Override Start Date / End Date (BravoDateEdit positions 1 and 2)
;       -> Ok
;   -> List renders with the full buy-ticket detail
;   -> Export the list to CSV (path discovered empirically; multiple attempts)
;   -> Cancel x2 back to Dashboard
;
; Trigger schema (single "date" string field, two supported encodings):
;   "date": "2026-05-14"                       — single day
;   "date": "2024-05-14..2026-04-30"           — explicit range (YYYY-MM-DD)
;
; Output CSV columns: whatever the saved report's column layout exports.
; Expected: Ticket #, Customer Name, Buy Amount, Status, Item Description,
; Store Location, Employee (per Joshua's saved template).
;
; ⚠️ The saved-report name string is set in BUYS_ELEMENTS below. If Joshua
;    named it something other than the placeholder, update the constant.
;
; ⚠️ The export-to-CSV path on a Custom Report list view is not used by any
;    existing handler. TryExportListToCsv tries several known patterns; on
;    failure it dumps LogVisibleNames so we can see the actual UI element
;    names and refine.
; ============================================================================

#Requires AutoHotkey v2.0

global BUYS_ELEMENTS := Map(
    "sidebar_loans_buys",   "Loans/Buys",
    "panel_custom_reports", "Custom Reports",
    "saved_report_combo",   "Choose Saved Report",
    "saved_report_value",   "Claude Buy Reviews",
    "dialog_ok",            "Ok",
    "panel_cancel",         "Cancel",
    "layouts_caret",        "Layouts"
)

PullBuysFromPublic(store, dateOrRange, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "buys-from-public",
        "store",       store,
        "date",        dateOrRange,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    ; --- Parse date range ---------------------------------------------------
    ; Accepts:
    ;   "YYYY-MM-DD"                       -> startDate = endDate = same day
    ;   "YYYY-MM-DD..YYYY-MM-DD"           -> explicit range
    startDate := ""
    endDate := ""
    if InStr(dateOrRange, "..") {
        parts := StrSplit(dateOrRange, "..")
        if (parts.Length != 2)
            return Fail(result, started, "Malformed date range: " . dateOrRange . " (expected YYYY-MM-DD..YYYY-MM-DD)")
        startDate := Trim(parts[1])
        endDate := Trim(parts[2])
    } else {
        startDate := dateOrRange
        endDate := dateOrRange
    }
    LogMessage("[" . store . "] BuysFromPublic startDate=" . startDate . " endDate=" . endDate)

    ; Output filename includes the explicit range so weekly and cumulative
    ; runs don't collide.
    outputFileName := startDate . "_to_" . endDate . "_" . store . "_buys-from-public.csv"
    outputPath := outputDir . "\" . outputFileName
    LogMessage("  output -> " . outputPath)

    ; Lenient wait: only require that the Bravo window exists, not that it's
    ; on a store dashboard. If Bravo is at Global Access / locked / showing a
    ; dialog, EnsureStore handles the recovery (login flow, session resume).
    ; The strict WaitForBravoReady that requires "VALLEY PAWN - " in the title
    ; was getting the handler stuck when Bravo timed out between runs.
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

    ; ------------------------------------------------------------------
    ; Pre-dismiss any stuck modal dialogs from prior runs before letting
    ; BackToDashboard try its own strategies. Bravo's btnCancel/InvokePattern
    ; combination can get into a state where the lib's Click("left") doesn't
    ; actually dismiss the dialog (seen 2026-05-14 across multiple smoke
    ; tests). Two-pronged approach:
    ;   1. Walk all visible Buttons with AutomationId="btnCancel" or "PART_CancelDialogButton"
    ;      and Invoke them explicitly via UIA pattern (more reliable than Click).
    ;   2. Send Esc as a final fallback.
    ; This is idempotent — if no dialogs are open, both passes no-op.
    ; ------------------------------------------------------------------
    ActivateBravo()
    Loop 4 {
        dismissed := false
        try {
            root := GetBravoRoot()
            ; Find btnCancel (Bravo dialog Cancel)
            cancelEl := root.FindElement({AutomationId: "btnCancel"})
            if cancelEl {
                try {
                    cancelEl.InvokePattern.Invoke()
                    LogMessage("    [pre-dismiss] Invoked btnCancel via InvokePattern")
                    dismissed := true
                } catch as ie {
                    LogMessage("    [pre-dismiss] InvokePattern threw: " . ie.Message . " — trying Click")
                    try {
                        cancelEl.Click("left")
                        dismissed := true
                    }
                }
                Sleep(900)
            }
        }
        ; Also try PART_CancelDialogButton (DevExpress generic cancel)
        try {
            root := GetBravoRoot()
            cancelEl := root.FindElement({AutomationId: "PART_CancelDialogButton"})
            if cancelEl {
                try {
                    cancelEl.InvokePattern.Invoke()
                    LogMessage("    [pre-dismiss] Invoked PART_CancelDialogButton")
                    dismissed := true
                    Sleep(900)
                }
            }
        }
        if (!dismissed)
            break
    }
    ; Final Esc fallback (cheap, harmless if already on Dashboard)
    Sleep(300)

    if !BackToDashboard()
        return Fail(result, started, "BackToDashboard could not return Bravo to Dashboard")
    Sleep(500)
    DismissPopups()

    try {
        DismissPopups()

        LogMessage("  step 1: open Loans/Buys")
        ClickByName(BUYS_ELEMENTS["sidebar_loans_buys"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: click Custom Reports")
        ClickByName(BUYS_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(1500)

        LogMessage("  step 3: select saved report '" . BUYS_ELEMENTS["saved_report_value"] . "'")
        SelectSavedReport(BUYS_ELEMENTS["saved_report_combo"], BUYS_ELEMENTS["saved_report_value"])
        Sleep(1000)

        ; --- Override the date range -----------------------------------------
        ; The saved template carries a Transaction Date between-range filter.
        ; After loading, the dialog should expose two BravoDateEdit wrappers
        ; (Start position 1, End position 2) per the existing SetReportDate
        ; convention. If the dialog layout differs from EmployeeActivity's,
        ; SetReportDate will throw and we'll see LogVisibleNames output for
        ; the first-run diagnostic.
        LogMessage("  step 4: override Start Date to " . startDate)
        try {
            SetReportDate(1, startDate)
        } catch as e {
            LogMessage("    WARN: SetReportDate(1) failed: " . e.Message)
            LogVisibleNames()
            throw Error("Could not set Start Date — see LogVisibleNames dump")
        }
        Sleep(400)

        LogMessage("  step 5: override End Date to " . endDate)
        try {
            SetReportDate(2, endDate)
        } catch as e {
            LogMessage("    WARN: SetReportDate(2) failed: " . e.Message)
            LogVisibleNames()
            throw Error("Could not set End Date — see LogVisibleNames dump")
        }
        Sleep(400)

        LogMessage("  step 6: click Ok to run report")
        ClickByName(BUYS_ELEMENTS["dialog_ok"], 5000)

        ; Wait for list to render. Layouts caret only appears once the data
        ; grid is loaded. Same pattern as ChekkitInactives.
        if !FindByName(BUYS_ELEMENTS["layouts_caret"], 30000)
            throw Error("Buys list did not render within 30s (no Layouts caret)")
        ; DevExpress data grid takes 3-5s to populate rows after layout renders.
        Sleep(5000)
        DismissPopups()

        ; --- Walk the grid and write CSV ourselves ---------------------------
        ; Bravo's Loans/Buys Custom Reports list view does NOT expose an export-
        ; to-CSV button (only Layouts -> Show summary panel / Saved Layouts /
        ; Delete Layout). Same constraint as the Customers Custom Reports view.
        ; The proven workaround (see ChekkitInactives.ahk) is to walk the
        ; DevExpress grid cells (Text elements with AutoId=PART_Content), group
        ; them by Y into rows, and write the CSV ourselves.
        LogMessage("  step 7: walk grid rows and write CSV")
        rowsWritten := WriteBuysGridToCsv(outputPath)
        if (rowsWritten < 0) {
            LogVisibleNames()
            throw Error("Failed to walk buys grid (no PART_Content cells found)")
        }
        LogMessage("    wrote " . rowsWritten . " data rows to CSV")
        result["row_count"] := rowsWritten

        ; Back to Dashboard
        try ClickByName(BUYS_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        try ClickByName(BUYS_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)

    } catch as e {
        LogVisibleNames()
        return Fail(result, started, "UIA click sequence failed: " . e.Message)
    }

    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: " . result["row_count"] . " data rows, " . result["duration_ms"] . "ms")
    return result
}

; ----------------------------------------------------------------------------
; Walk the rendered DevExpress data grid in the Loans/Buys Custom Reports list
; view and write each row to a CSV. Modeled directly on WriteChekkitGridToCsv
; in ChekkitInactives.ahk — Bravo's Custom Reports lists don't expose an
; Export-to-CSV button, so the proven workaround is UIA grid walking.
;
; Cells in the data grid expose as UIA Text elements with
; AutomationId="PART_Content". Their Name property holds the cell's display
; value. We group cells by Y coordinate (same row), order by X within each row,
; and write to CSV. The first row that looks like the column header (matches
; a known label) is used to derive the CSV header line and skipped from data.
;
; Returns the number of data rows written, or -1 on failure.
; ----------------------------------------------------------------------------
WriteBuysGridToCsv(outputPath) {
    ; Bravo's Loans/Buys grid (LoanManagementView) uses DataItem control type
    ; for each visible row. Children have AutomationId matching the column
    ; name (TicketNumber/Category/FullDescription/LoanAmount/etc.). The child's
    ; Name is an accessibility string of the form:
    ;   "Row N of TOTAL, Column LABEL, Column X of Y: VALUE"
    ; We extract the VALUE after the last ": " separator. AutomationId is the
    ; canonical column key. TOTAL is read from the accessibility string and
    ; tells us how many rows to expect.
    ;
    ; The grid is virtualized — only ~22 rows are rendered at a time. To
    ; capture all rows, we PageDown through the grid, dedupe by rowIndex,
    ; and stop when we've seen all TOTAL rows (or when 3 consecutive
    ; PageDowns find no new rows, as a safety stop).

    allRows := Map()          ; rowIndex -> { autoId -> value }
    columnAutoIds := []
    columnLabels := Map()
    totalRows := -1
    pagesNoNewRows := 0
    maxPages := 250           ; safety: caps at ~5500 rows
    pageIdx := 0

    ; Focus the grid by clicking on a known-visible DataItem first, so
    ; PageDown actually scrolls the data area instead of e.g. the sidebar.
    try {
        root := GetBravoRoot()
        firstDi := root.FindElement({Type: "DataItem"})
        if firstDi {
            try firstDi.Click("left")
            Sleep(200)
        }
    }

    Loop maxPages {
        pageIdx++
        ; Enumerate current visible DataItems
        dataItems := 0
        try {
            root := GetBravoRoot()
            dataItems := root.FindElements({Type: "DataItem"})
        } catch as e {
            LogMessage("    WARN scroll pass " . pageIdx . " enumerate: " . e.Message)
            break
        }
        if (!dataItems || dataItems.Length = 0) {
            LogMessage("    [grid] no DataItems on pass " . pageIdx)
            break
        }

        newRowsThisPass := 0
        for di in dataItems {
            kids := 0
            try kids := di.FindElements({Scope: 2})
            if (!kids || kids.Length = 0)
                continue

            ; Find this row's index from any child's accessibility name.
            rowIdx := -1
            for k in kids {
                kName := ""
                try kName := k.Name
                if RegExMatch(kName, "Row (\d+) of (\d+)", &m) {
                    rowIdx := Integer(m[1])
                    rt := Integer(m[2])
                    if (totalRows < 0 || rt > totalRows)
                        totalRows := rt
                    break
                }
            }
            if (rowIdx < 0)
                continue
            if (allRows.Has(rowIdx))
                continue  ; already captured this row in a prior pass

            ; Capture this row
            rowMap := Map()
            for k in kids {
                kAutoId := ""
                kName := ""
                try kAutoId := k.AutomationId
                try kName := k.Name
                if (kAutoId = "")
                    continue
                if (!columnLabels.Has(kAutoId)) {
                    columnAutoIds.Push(kAutoId)
                    lbl := kAutoId
                    if RegExMatch(kName, "Column ([^,]+), Column \d+ of \d+", &mc)
                        lbl := mc[1]
                    columnLabels[kAutoId] := lbl
                }
                v := kName
                colonPos := InStr(kName, ": ", false, -1)
                if (colonPos > 0)
                    v := SubStr(kName, colonPos + 2)
                rowMap[kAutoId] := v
            }
            allRows[rowIdx] := rowMap
            newRowsThisPass++
        }

        LogMessage("    [grid pass " . pageIdx . "] new=" . newRowsThisPass . " seen=" . allRows.Count . "/" . (totalRows > 0 ? totalRows : "?"))

        ; Stop conditions
        if (totalRows > 0 && allRows.Count >= totalRows) {
            LogMessage("    [grid] captured all " . totalRows . " rows")
            break
        }
        if (newRowsThisPass = 0) {
            pagesNoNewRows++
            if (pagesNoNewRows >= 3) {
                LogMessage("    [grid] 3 consecutive PageDowns with no new rows; stopping at " . allRows.Count)
                break
            }
        } else {
            pagesNoNewRows := 0
        }

        ; Scroll down — PageDown sent to focused grid. 400ms is enough for
        ; DevExpress grid to render the next page in WPF.
        Send("{PgDn}")
        Sleep(400)
    }

    if (allRows.Count = 0 || columnAutoIds.Length = 0) {
        LogMessage("    no rows / columns captured")
        return -1
    }

    ; Write CSV header
    headerLine := ""
    for i, autoId in columnAutoIds {
        if (i > 1)
            headerLine .= ","
        headerLine .= ToCsvField(columnLabels[autoId])
    }
    FileAppend(headerLine . "`r`n", outputPath, "UTF-8-RAW")
    LogMessage("    [grid] header: " . headerLine)

    ; Sort row indices ascending
    sortedIdx := []
    for idx, _ in allRows
        sortedIdx.Push(idx)
    n := sortedIdx.Length
    i := 2
    while (i <= n) {
        j := i
        while (j > 1 && sortedIdx[j] < sortedIdx[j-1]) {
            tmp := sortedIdx[j]
            sortedIdx[j] := sortedIdx[j-1]
            sortedIdx[j-1] := tmp
            j--
        }
        i++
    }

    ; Write rows in order
    dataCount := 0
    for idx in sortedIdx {
        r := allRows[idx]
        rowLine := ""
        for i, autoId in columnAutoIds {
            if (i > 1)
                rowLine .= ","
            v := r.Has(autoId) ? r[autoId] : ""
            rowLine .= ToCsvField(v)
        }
        FileAppend(rowLine . "`r`n", outputPath, "UTF-8-RAW")
        dataCount++
    }
    return dataCount
}

; Old grid-walking implementation (kept for diagnostic reference; not used).
; Returns -1 always so caller falls through if accidentally called.
WriteBuysGridToCsv_LegacyByPartContent(outputPath) {
    cells := []
    try {
        root := GetBravoRoot()
        texts := root.FindElements({Type: "Text"})
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
            xVal := 0
            yVal := 0
            try xVal := rect.l
            try yVal := rect.t
            cells.Push(Map("name", n, "x", xVal, "y", yVal))
        }
        LogMessage("    [grid-legacy] PART_Content Text cells found: " . cells.Length)
    } catch as e {
        LogMessage("    WARN WriteBuysGridToCsv_legacy enumerate: " . e.Message)
        return -1
    }

    ; --- Diagnostic dump if cell count is suspiciously low ---
    ; A populated buy report should have dozens to hundreds of cells; if we
    ; have <= 4 cells we likely only have the header row and missed the data.
    ; Dump grid structure clues so we know what AutoId / control type the
    ; data rows use.
    if (cells.Length <= 8) {
        LogMessage("    [grid-diag] suspiciously few cells (" . cells.Length . ") — dumping grid structure")
        try {
            root := GetBravoRoot()
            ; Count DataItem (typical for DevExpress data rows)
            dataItems := root.FindElements({Type: "DataItem"})
            LogMessage("    [grid-diag] DataItem total: " . (dataItems ? dataItems.Length : 0))
            if (dataItems && dataItems.Length > 0) {
                ; Sample the first 3 DataItem names + their children
                showCount := 0
                for di in dataItems {
                    showCount++
                    if (showCount > 3)
                        break
                    diName := ""
                    diAutoId := ""
                    try diName := di.Name
                    try diAutoId := di.AutomationId
                    LogMessage("    [grid-diag] DataItem[" . showCount . "] name='" . SubStr(diName, 1, 80) . "' autoId='" . diAutoId . "'")
                    ; Walk children
                    try {
                        kids := di.FindElements({Scope: "Children"})
                        kidShowCount := 0
                        for k in kids {
                            kidShowCount++
                            if (kidShowCount > 6)
                                break
                            kName := ""
                            kAutoId := ""
                            kClass := ""
                            try kName := k.Name
                            try kAutoId := k.AutomationId
                            try kClass := k.ClassName
                            LogMessage("    [grid-diag]   child name='" . SubStr(kName, 1, 60) . "' autoId='" . kAutoId . "' class='" . kClass . "'")
                        }
                    }
                }
            }
            ; Also try ListItem
            listItems := root.FindElements({Type: "ListItem"})
            LogMessage("    [grid-diag] ListItem total: " . (listItems ? listItems.Length : 0))
            ; And Custom controls
            customs := root.FindElements({Type: "Custom"})
            LogMessage("    [grid-diag] Custom controls total: " . (customs ? customs.Length : 0))

            ; Sample Text elements with their AutoIds to see what's there
            allTexts := root.FindElements({Type: "Text"})
            LogMessage("    [grid-diag] Text total: " . (allTexts ? allTexts.Length : 0))
            autoIdSet := Map()
            for t in allTexts {
                a := ""
                try a := t.AutomationId
                if (a = "")
                    continue
                if (!autoIdSet.Has(a))
                    autoIdSet[a] := 0
                autoIdSet[a] := autoIdSet[a] + 1
            }
            autoIdSummary := ""
            for k, v in autoIdSet {
                autoIdSummary .= k . "(" . v . ") "
            }
            LogMessage("    [grid-diag] Text AutoIds in use: " . autoIdSummary)
        } catch as e {
            LogMessage("    [grid-diag] diag failed: " . e.Message)
        }
    }

    if (cells.Length = 0) {
        LogMessage("    no PART_Content cells found")
        return -1
    }

    ; Sort by Y then X (insertion sort, small N).
    n := cells.Length
    i := 2
    while (i <= n) {
        j := i
        while (j > 1) {
            a := cells[j]
            b := cells[j - 1]
            if (a["y"] < b["y"] || (a["y"] = b["y"] && a["x"] < b["x"])) {
                cells[j] := b
                cells[j - 1] := a
                j--
            } else {
                break
            }
        }
        i++
    }

    ; Group cells into rows by Y (within ±8 pixels = same row).
    rows := []
    currentRow := []
    currentY := -99999
    yTolerance := 8
    for c in cells {
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

    if (rows.Length = 0) {
        LogMessage("    no rows assembled from cells")
        return -1
    }

    ; Identify the header row by matching known column labels. The saved
    ; "Claude Buy Reviews" template includes Ticket Number / Customer Name /
    ; Buy Amount / Status / Item Description / Store Location / Employee. The
    ; column labels in the grid header may differ slightly (e.g. "Number" vs
    ; "Ticket Number") — match on substrings.
    headerHints := ["Number", "Ticket", "Customer", "Amount", "Status", "Item Description", "Description", "Store", "Location", "Employee", "Associate"]
    headerRowIdx := 0
    for idx, r in rows {
        matchCount := 0
        for cell in r {
            if (cell = "")
                continue
            for hint in headerHints {
                if (InStr(cell, hint)) {
                    matchCount++
                    break
                }
            }
        }
        if (matchCount >= 3) {
            headerRowIdx := idx
            break
        }
    }

    ; Write CSV. Use the header row's cells as the column line if found;
    ; otherwise emit a generic header.
    if (headerRowIdx > 0) {
        headerRow := rows[headerRowIdx]
        FileAppend(JoinCsvRow(headerRow) . "`r`n", outputPath, "UTF-8-RAW")
        LogMessage("    [grid] header row (index " . headerRowIdx . "): " . JoinCsvRow(headerRow))
    } else {
        FileAppend("col1,col2,col3,col4,col5,col6,col7`r`n", outputPath, "UTF-8-RAW")
        LogMessage("    [grid] WARN: header row not identified; using generic col1..col7")
    }

    ; Write data rows (skip header, skip rows where all cells are empty).
    dataCount := 0
    for idx, r in rows {
        if (idx <= headerRowIdx)
            continue
        ; Skip empty rows
        allEmpty := true
        for c in r {
            if (c != "") {
                allEmpty := false
                break
            }
        }
        if (allEmpty)
            continue
        FileAppend(JoinCsvRow(r) . "`r`n", outputPath, "UTF-8-RAW")
        dataCount++
    }
    return dataCount
}

; Join a list of cell strings into a CSV row, applying ToCsvField quoting
; from lib/Bravo.ahk.
JoinCsvRow(cells) {
    line := ""
    for i, c in cells {
        if (i > 1)
            line .= ","
        line .= ToCsvField(c)
    }
    return line
}

; Lenient version of WaitForBravoReady — only requires that a Bravo window
; exists, without requiring "VALLEY PAWN - " in its title. This lets the
; handler proceed when Bravo is at Global Access / locked / etc, and trust
; EnsureStore to do the login flow from there.
WaitForBravoWindowExists(timeoutSec := 30) {
    deadline := A_TickCount + timeoutSec * 1000
    loop {
        if WinExist(BRAVO_WIN_TITLE)
            return true
        if (A_TickCount > deadline)
            return false
        Sleep(500)
    }
}
