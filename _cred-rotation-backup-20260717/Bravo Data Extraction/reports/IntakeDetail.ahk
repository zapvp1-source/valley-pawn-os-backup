; ============================================================================
; reports/IntakeDetail.ahk
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
; ⚠️ The saved-report name string is set in INTAKE_ELEMENTS below. If Joshua
;    named it something other than the placeholder, update the constant.
;
; ⚠️ The export-to-CSV path on a Custom Report list view is not used by any
;    existing handler. TryExportListToCsv tries several known patterns; on
;    failure it dumps LogVisibleNames so we can see the actual UI element
;    names and refine.
; ============================================================================

#Requires AutoHotkey v2.0

global INTAKE_ELEMENTS := Map(
    "sidebar_loans_buys",   "Loans/Buys",
    "panel_custom_reports", "Custom Reports",
    "saved_report_combo",   "Choose Saved Report",
    "saved_report_value",   "Claude Pawn Walks",
    "dialog_ok",            "Ok",
    "panel_cancel",         "Cancel",
    "layouts_caret",        "Layouts"
)

PullIntakeDetail(store, dateOrRange, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "intake-detail",
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
    LogMessage("[" . store . "] IntakeDetail startDate=" . startDate . " endDate=" . endDate)

    ; Output filename includes the explicit range so weekly and cumulative
    ; runs don't collide.
    outputFileName := startDate . "_to_" . endDate . "_" . store . "_intake-detail.csv"
    outputPath := outputDir . "\" . outputFileName
    LogMessage("  output -> " . outputPath)

    ; Lenient wait: only require that the Bravo window exists, not that it's
    ; on a store dashboard. If Bravo is at Global Access / locked / showing a
    ; dialog, EnsureStore handles the recovery (login flow, session resume).
    ; The strict WaitForBravoReady that requires "VALLEY PAWN - " in the title
    ; was getting the handler stuck when Bravo timed out between runs.
    if !WaitForIntakeBravoWin(30)
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
        ClickByName(INTAKE_ELEMENTS["sidebar_loans_buys"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: click Custom Reports")
        ClickByName(INTAKE_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(1500)

        ; --- Select + run + verify-by-COLUMNS, retry whole selection -------
        ; 2026-06-30 (per Joshua: "on some you are not clicking the right
        ; report"). After a store SWITCH, the saved-report click can silently
        ; leave the DEFAULT loan layout loaded (cols Ticket Number/Disposition/
        ; Age/Due Date) instead of Claude Pawn Walks (Category/Full Description).
        ; BoxReportName is empty on BOTH success and failure, so it cannot tell
        ; them apart. The reliable signal is the rendered columns: the Pawn Walk
        ; report exposes DataItem children with AutoId FullDescription/Category;
        ; the default loan layout does not. So: select -> Ok -> check columns;
        ; if wrong, dismiss + reopen Custom Reports + re-select, up to 3 tries.
        gridReady := false
        Loop 3 {
            selAttempt := A_Index
            LogMessage("  step 3: select saved report '" . INTAKE_ELEMENTS["saved_report_value"] . "' (attempt " . selAttempt . ")")
            IntakeSelectSavedReportCommitted(INTAKE_ELEMENTS["saved_report_combo"], INTAKE_ELEMENTS["saved_report_value"])
            Sleep(1000)
            loadedName := IntakeGetLoadedReportName()
            LogMessage("    [saved-report] BoxReportName=" . Chr(39) . loadedName . Chr(39))

            LogMessage("  step 4-5: skipping date override (report uses Age=1)")
            Sleep(4000)
            LogMessage("  step 6: click Ok to run report (verified)")
            IntakeClickOkVerified()

            if !FindByName(INTAKE_ELEMENTS["layouts_caret"], 30000)
                throw Error("Buys list did not render within 30s (no Layouts caret)")
            Sleep(5000)

            ; Verify the CORRECT report by its item-detail columns.
            Loop 20 {
                items := 0
                try {
                    root := GetBravoRoot()
                    items := root.FindElements({Type: "DataItem"})
                }
                if (items && items.Length) {
                    for di in items {
                        kids := 0
                        try kids := di.FindElements({Scope: 2})
                        if (!kids || !kids.Length)
                            continue
                        for k in kids {
                            kAutoId := ""
                            try kAutoId := k.AutomationId
                            if (kAutoId = "FullDescription" || kAutoId = "Category") {
                                gridReady := true
                                break
                            }
                        }
                        if (gridReady)
                            break
                    }
                }
                if (gridReady)
                    break
                Sleep(800)
            }
            if (gridReady) {
                LogMessage("    [layout] correct report confirmed (item cols) on attempt " . selAttempt)
                break
            }

            ; Wrong report loaded -> dismiss and re-select (unless out of tries).
            LogMessage("    WARN: wrong report loaded (no item cols) - re-selecting, attempt " . selAttempt)
            try ClickByName(INTAKE_ELEMENTS["panel_cancel"], 3000)
            Sleep(800)
            try ClickByName(INTAKE_ELEMENTS["panel_cancel"], 3000)
            Sleep(800)
            if (selAttempt < 3) {
                if !BackToDashboard()
                    throw Error("could not return to Dashboard between selection retries")
                Sleep(500)
                DismissPopups()
                LogMessage("  re-open Loans/Buys + Custom Reports for re-selection")
                ClickByName(INTAKE_ELEMENTS["sidebar_loans_buys"], 8000)
                Sleep(1500)
                DismissPopups()
                ClickByName(INTAKE_ELEMENTS["panel_custom_reports"], 5000)
                Sleep(1500)
            }
        }
        if (!gridReady)
            throw Error("Claude Pawn Walks did not load after 3 selection attempts (wrong report / no item columns)")
        LogMessage("    [layout] item-detail columns present in grid (FullDescription/Category)")
        DismissPopups()

        ; --- Walk the grid and write CSV ourselves ---------------------------
        ; Bravo's Loans/Buys Custom Reports list view does NOT expose an export-
        ; to-CSV button (only Layouts -> Show summary panel / Saved Layouts /
        ; Delete Layout). Same constraint as the Customers Custom Reports view.
        ; The proven workaround (see ChekkitInactives.ahk) is to walk the
        ; DevExpress grid cells (Text elements with AutoId=PART_Content), group
        ; them by Y into rows, and write the CSV ourselves.
        LogMessage("  step 7: walk grid rows and write CSV")
        rowsWritten := WriteIntakeDetailGrid(outputPath)
        if (rowsWritten < 0) {
            LogVisibleNames()
            throw Error("Failed to walk buys grid (no PART_Content cells found)")
        }
        LogMessage("    wrote " . rowsWritten . " data rows to CSV")
        result["row_count"] := rowsWritten

        ; Back to Dashboard
        try ClickByName(INTAKE_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        try ClickByName(INTAKE_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)

    } catch as e {
        LogVisibleNames()
        ; Close the Loans/Buys screen before failing - a leftover open screen
        ; blocks the next store switch ("Cannot switch stores: ... is busy
        ; with Loans/Buys"), which cascades into EnsureStore failures.
        IntakeCloseReportScreen()
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
WriteIntakeDetailGrid(outputPath) {
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

    ; Discover a UIA scroll container (ScrollPattern) for the data grid. The
    ; summary-panel grid does NOT respond to PgDn/Down keystrokes, so we drive
    ; it via ScrollPattern.SetScrollPercent instead (focus-independent). Walk up
    ; from a DataItem to the nearest scrollable ancestor. (2026-06-16)
    scrollPct := 0
    scrollContainer := 0
    try {
        probe := root.FindElement({Type: "DataItem"})
        anc := probe
        Loop 10 {
            anc := anc.Parent
            if !anc
                break
            if anc.IsScrollPatternAvailable {
                scrollContainer := anc
                break
            }
        }
    }
    LogMessage("    [grid] scroll container: " . (scrollContainer ? "ScrollPattern" : "none - keyboard fallback"))
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
            if (pagesNoNewRows >= 5) {
                LogMessage("    [grid] 3 consecutive PageDowns with no new rows; stopping at " . allRows.Count)
                break
            }
        } else {
            pagesNoNewRows := 0
        }

        ; Advance the virtualized grid. The summary-panel grid ignores
        ; PgDn/Down keystrokes, so prefer UIA ScrollPattern (focus- and
        ; coordinate-independent). Fall back to keyboard if no scroll
        ; container was found. (2026-06-16)
        if scrollContainer {
            scrollPct := scrollPct + 18
            if (scrollPct > 100)
                scrollPct := 100
            try scrollContainer.ScrollPattern.SetScrollPercent(scrollPct, -1)
            Sleep(550)
        } else {
            try {
                rootS := GetBravoRoot()
                disS := rootS.FindElements({Type: "DataItem"})
                if (disS && disS.Length > 0)
                    try disS[disS.Length].Click("left")
            }
            Sleep(150)
            Send("{PgDn}")
            Sleep(500)
        }
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
WriteIntakeDetailGrid_LegacyByPartContent(outputPath) {
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
        LogMessage("    WARN WriteIntakeDetailGrid_legacy enumerate: " . e.Message)
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
    ; "Claude Pawn Walks" template includes Ticket Number / Customer Name /
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
        FileAppend(JoinIntakeCsvRow(headerRow) . "`r`n", outputPath, "UTF-8-RAW")
        LogMessage("    [grid] header row (index " . headerRowIdx . "): " . JoinIntakeCsvRow(headerRow))
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
        FileAppend(JoinIntakeCsvRow(r) . "`r`n", outputPath, "UTF-8-RAW")
        dataCount++
    }
    return dataCount
}

; Join a list of cell strings into a CSV row, applying ToCsvField quoting
; from lib/Bravo.ahk.
JoinIntakeCsvRow(cells) {
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
WaitForIntakeBravoWin(timeoutSec := 30) {
    deadline := A_TickCount + timeoutSec * 1000
    loop {
        if WinExist(BRAVO_WIN_TITLE)
            return true
        if (A_TickCount > deadline)
            return false
        Sleep(500)
    }
}


; ----------------------------------------------------------------------------
; 2026-06-12 fix: on some stores (observed LEX/WAY) the loaded saved report's
; Transaction Date criteria cells do NOT instantiate BravoDateEdit controls -
; they expose as PopupBaseEdit (AutoId=PART_Editor) until the cell is
; activated. Strategy: click the editor at the given x-position (1=start,
; 2=end) to activate it, retry the standard SetReportDate path, and if the
; control still is not a BravoDateEdit, set the popup editor directly via
; ValuePattern, then clipboard paste as last resort.
IntakeSetDateByPopupEditor(position, yyyymmdd) {
    parts := StrSplit(yyyymmdd, "-")
    if (parts.Length != 3)
        throw Error("malformed date " . yyyymmdd)
    bravoDate := Integer(parts[2]) . "/" . Integer(parts[3]) . "/" . parts[1]

    el := IntakeFindPopupDateEditor(position)
    if !el
        throw Error("no PopupBaseEdit PART_Editor found at position " . position)

    try el.Click("left")
    Sleep(500)

    ; Activation may have instantiated a real BravoDateEdit - retry standard path.
    try {
        SetReportDate(position, yyyymmdd)
        LogMessage("    [date-fallback] standard path succeeded after cell activation (position " . position . ")")
        return
    }

    ; Re-find: the reference can go stale after activation.
    el := IntakeFindPopupDateEditor(position)
    if !el
        throw Error("popup editor vanished after activation (position " . position . ")")

    try {
        el.Value := bravoDate
        Sleep(150)
        Send("{Tab}")
        Sleep(150)
        LogMessage("    [date-fallback] position=" . position . " set to " . bravoDate . " via ValuePattern")
        return
    } catch as e {
        LogMessage("    WARN [date-fallback] ValuePattern failed: " . e.Message . " - trying clipboard")
    }

    try el.Focus()
    Sleep(200)
    A_Clipboard := bravoDate
    ClipWait(2)
    Send("^a")
    Sleep(100)
    Send("^v")
    Sleep(200)
    Send("{Tab}")
    Sleep(150)
    LogMessage("    [date-fallback] position=" . position . " pasted via clipboard")
}

; Find the Nth (by x ascending) Edit named 'PopupBaseEdit' with
; AutomationId=PART_Editor. Returns the element or 0.
IntakeFindPopupDateEditor(position) {
    wrappers := []
    try {
        root := GetBravoRoot()
        edits := root.FindElements({Type: "Edit"})
        for e in edits {
            n := ""
            try n := e.Name
            if (n != "PopupBaseEdit")
                continue
            autoId := ""
            try autoId := e.AutomationId
            if (autoId != "PART_Editor")
                continue
            rect := 0
            try rect := e.BoundingRectangle
            if !rect
                continue
            wrappers.Push(Map("elem", e, "x", rect.l))
        }
    } catch as ex {
        LogMessage("    WARN IntakeFindPopupDateEditor: " . ex.Message)
        return 0
    }
    if (wrappers.Length < position)
        return 0
    ; selection sort by x ascending
    Loop wrappers.Length {
        i := A_Index
        minIdx := i
        j := i + 1
        while (j <= wrappers.Length) {
            if (wrappers[j]["x"] < wrappers[minIdx]["x"])
                minIdx := j
            j++
        }
        if (minIdx != i) {
            tmp := wrappers[i]
            wrappers[i] := wrappers[minIdx]
            wrappers[minIdx] := tmp
        }
    }
    return wrappers[position]["elem"]
}

; Best-effort: dismiss dialogs and close the Loans/Buys screen so a failed
; cell can never leave Bravo "busy with Loans/Buys" and block the next store.
IntakeCloseReportScreen() {
    try DismissPopups()
    Loop 2 {
        try ClickByName(INTAKE_ELEMENTS["panel_cancel"], 2000)
        Sleep(700)
    }
    try DismissPopups()
    try BackToDashboard()
    Sleep(500)
}


; Read the Custom Reports dialog's report-name box (AutoId=BoxReportName).
; Returns "" if not found / unreadable.
IntakeGetLoadedReportName() {
    try {
        root := GetBravoRoot()
        el := root.FindElement({AutomationId: "BoxReportName"})
        if el {
            v := ""
            try v := el.Value
            return v
        }
    }
    return ""
}


; 2026-06-30: "Claude Pawn Walks" sits LOWER in the saved-report dropdown,
; below the visible rows (Joshua: "you have to scroll down a little to find it").
; The list is alphabetical and VIRTUALIZED -- the row is not rendered (so
; ClickByName cannot reach it) until the list scrolls down to it. A plain
; ClickByName therefore never committed on store-switched stores, leaving the
; default loan layout loaded. Fix (human-style): open the dropdown, then arrow
; DOWN to scroll, attempting to click the target row each step; the click lands
; the instant the row scrolls into view and commits the selection. The shared
; SelectSavedReport is left untouched so Loans75/Layaways keep working.
IntakeSelectSavedReportCommitted(comboName, valueName) {
    combo := FindSavedReportCombo()
    if !combo
        combo := FindByName(comboName, 1500)
    if !combo
        throw Error("IntakeSelectSavedReport: could not locate saved-report combo")
    CoordMode("Mouse", "Screen")
    ActivateBravo()
    try combo.Click("left")          ; open the dropdown
    Sleep(900)
    crect := 0
    try crect := combo.BoundingRectangle
    selected := false
    ; The dropdown row must be committed with a GENUINE mouse click -- a UIA
    ; Click finds the row but does not register as a selection in this DevExpress
    ; combo (the report never loads; the default 250-row list does). So render
    ; the row on-screen, then do a real Click at its coordinates (Joshua showed
    ; this is what commits it; the combo value then reads the report name).
    ; Method 1: ScrollIntoView then real-click if on-screen.
    el := FindByName(valueName, 1500)
    if (el) {
        try el.ScrollIntoView()
        Sleep(450)
        r := 0
        try r := el.BoundingRectangle
        if (r && r.b > r.t && r.t > 0 && crect && r.b <= crect.t + 10) {
            ecx := (r.l + r.r) // 2
            ecy := (r.t + r.b) // 2
            MouseMove(ecx, ecy, 10)
            Sleep(150)
            Click(ecx, ecy)
            Sleep(700)
            selected := true
            LogMessage("    [saved-report] ScrollIntoView+REAL-clicked '" . valueName . "' at " . ecx . "," . ecy)
        }
    }
    ; Method 2: wheel-scroll the open list, real-click when the row is on-screen.
    if (!selected && crect) {
        cx := (crect.l + crect.r) // 2
        listY := crect.t - 120
        MouseMove(cx, listY, 0)
        Sleep(200)
        Loop 26 {
            el2 := FindByName(valueName, 150)
            if (el2) {
                r2 := 0
                try r2 := el2.BoundingRectangle
                if (r2 && r2.b > r2.t && r2.t > 0 && r2.b <= crect.t + 10) {
                    ecx := (r2.l + r2.r) // 2
                    ecy := (r2.t + r2.b) // 2
                    MouseMove(ecx, ecy, 10)
                    Sleep(120)
                    Click(ecx, ecy)
                    Sleep(700)
                    selected := true
                    LogMessage("    [saved-report] wheel+REAL-clicked '" . valueName . "' after " . (A_Index - 1) . " wheel-downs")
                    break
                }
            }
            MouseMove(cx, listY, 0)
            Send("{WheelDown}")
            Sleep(220)
        }
    }
    cur := ""
    try cur := combo.Value
    LogMessage("    [saved-report] combo value now = '" . cur . "' (selected=" . (selected ? "1" : "0") . ")")
    if (!selected)
        LogMessage("    WARN: could not real-click '" . valueName . "'; downstream column-check will verify/retry")
    Sleep(1100)
}

; 2026-06-16: clicking Ok in the Loans/Buys report generator is unreliable -
; "Ok" is exposed as a Text label, not a named Button, so a single ClickByName
; can land without firing. Try several gestures and VERIFY the dialog actually
; closed (the "New Report" button exists only while the dialog is open).
IntakeClickOkVerified() {
    Loop 5 {
        i := A_Index
        btn := IntakeFindOkButton()
        if btn {
            try {
                if (Mod(i, 2) = 1)
                    btn.Click("left")
                else
                    btn.Invoke()
                LogMessage("    [ok] activated Ok button attempt " . i . " (" . (Mod(i, 2) = 1 ? "click" : "invoke") . ")")
            } catch as e {
                LogMessage("    WARN Ok activate attempt " . i . ": " . e.Message)
            }
        } else {
            ActivateBravo()
            Send("{Enter}")
            LogMessage("    [ok] Ok button not resolved; sent Enter attempt " . i)
        }
        Sleep(1800)
        if !ExistsByName("New Report") {
            LogMessage("    [ok] dialog closed after attempt " . i)
            return
        }
        LogMessage("    [ok] dialog still open after attempt " . i . " - escalating")
    }
    throw Error("Ok did not run the report (dialog stayed open)")
}

; Locate the report-generator's Ok button. In the Loans/Buys Custom Report
; dialog the Ok control is a NAMELESS Button with no AutomationId, sitting in
; the bottom button row immediately to the LEFT of the (named) Cancel button.
; "Ok" itself is only a Text label inside it, so ClickByName("Ok") grabs the
; label and the click never reaches the button. Find the button by geometry
; relative to Cancel so it survives window resizes. (2026-06-16)
IntakeFindOkButton() {
    root := GetBravoRoot()
    btns := 0
    try btns := root.FindElements({Type: "Button"})
    if !btns
        return 0
    cancelLeft := 0
    cancelTop := 0
    for el in btns {
        nm := "?"
        aid := "?"
        rc := 0
        try nm := el.Name
        try aid := el.AutomationId
        try rc := el.BoundingRectangle
        if (nm = "Cancel" && aid = "" && rc) {
            cancelLeft := rc.l
            cancelTop := rc.t
        }
    }
    if (cancelLeft = 0)
        return 0
    best := 0
    bestL := -1
    for el in btns {
        nm := "?"
        aid := "?"
        rc := 0
        try nm := el.Name
        try aid := el.AutomationId
        try rc := el.BoundingRectangle
        if (!rc)
            continue
        if (nm != "")
            continue
        if (aid != "")
            continue
        if (Abs(rc.t - cancelTop) > 40)
            continue
        if (rc.l >= cancelLeft)
            continue
        if (rc.l > bestL) {
            bestL := rc.l
            best := el
        }
    }
    return best
}
