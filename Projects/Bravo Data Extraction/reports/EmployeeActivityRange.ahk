; ============================================================================
; reports/EmployeeActivityRange.ahk
;
; ADDITIVE clone of EmployeeActivity.ahk (2026-09-05) that honours an explicit
; date RANGE. Pulls Bravo's "Employee Activity" report for a single store with
; Start Date = range start and End Date = range end, exports as CSV.
;
; Why: EmployeeActivity.ahk leaves End Date at "today", which is right for the
; weekly MTD board but wrong for a FINAL prior-month ranking pulled after the
; 1st (it would bleed the new month's sales in). The Sept 1 2026 monthly post
; had to be deleted for exactly this class of problem.
;
; Cell name: employee-activity-range
; Trigger `date`: "YYYY-MM-DD..YYYY-MM-DD"  (a single YYYY-MM-DD also works —
;   end date is then left at today, identical to employee-activity)
; Output: output/{END}_{STORE}_employee-activity-range.csv
;
; SKILL it powers: monthly-employee-sales-rankings (rebuilt 2026-09-05)
;
; Reuses SetReportDate / FindBravoDateEditByPosition from EmployeeActivity.ahk
; (which the watcher already #Includes) — do NOT redefine them here.
; ============================================================================

#Requires AutoHotkey v2.0

global EMPACTR_ELEMENTS := Map(
    "sidebar_reports",    "Reports",
    "report_tile",        "Employee Activity",
    "config_start_date",  "Start Date",
    "config_end_date",    "End Date",
    "config_ok",          "Ok",
    "preview_export",     "Export...",
    "export_ok",          "OK",
    "panel_done",         "Done"
)

PullEmployeeActivityRange(store, dateOrRange, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "employee-activity-range",
        "store",       store,
        "date",        dateOrRange,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    startDate := dateOrRange
    endDate := ""
    if InStr(dateOrRange, "..") {
        parts := StrSplit(dateOrRange, "..")
        if (parts.Length != 2)
            return Fail(result, started, "Malformed date range: " . dateOrRange . " (expected YYYY-MM-DD..YYYY-MM-DD)")
        startDate := parts[1]
        endDate := parts[2]
    }
    fileDate := (endDate != "") ? endDate : startDate

    outputPath := outputDir . "\" . OutputFilename(fileDate, store, "employee-activity-range")
    LogMessage("[" . store . "] EmployeeActivityRange start=" . startDate . " end=" . (endDate != "" ? endDate : "(today)") . " -> " . outputPath)

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

        LogMessage("  step 1: open Reports")
        ClickByName(EMPACTR_ELEMENTS["sidebar_reports"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: double-click Employee Activity tile (= Preview)")
        DoubleClickByName(EMPACTR_ELEMENTS["report_tile"], 8000)
        Sleep(2500)
        DismissPopups()

        LogMessage("  step 3: set Start Date")
        SetReportDate(EMPACTR_ELEMENTS["config_start_date"], startDate)

        if (endDate != "") {
            LogMessage("  step 3b: set End Date")
            SetReportDate(EMPACTR_ELEMENTS["config_end_date"], endDate)
        }

        LogMessage("  step 4: click config Ok")
        ClickByName(EMPACTR_ELEMENTS["config_ok"], 5000)

        ; A full calendar month renders slower than the weekly MTD preview —
        ; first live run (2026-09-05, CUL, 8/1..8/31) took ~50 s. 120 s budget.
        if !FindByName(EMPACTR_ELEMENTS["preview_export"], 120000)
            throw Error("Preview did not render within 120s")
        Sleep(500)

        LogMessage("  step 5: click Export Document")
        ClickByName(EMPACTR_ELEMENTS["preview_export"], 5000)
        if !FindByName(EMPACTR_ELEMENTS["export_ok"], 8000)
            throw Error("Export Document dialog did not appear within 8s")

        Sleep(800)
        SetExportFormatCsv()
        SetExportFilePath(outputPath)
        UncheckOpenAfterExport()
        ClickByName(EMPACTR_ELEMENTS["export_ok"], 5000)

        if !WaitForFile(outputPath, 30)
            throw Error("CSV file did not appear at " . outputPath . " within 30s")
        Sleep(500)

        try ClickByName(EMPACTR_ELEMENTS["panel_done"], 3000)
        Sleep(800)
        try ClickByName(EMPACTR_ELEMENTS["panel_done"], 3000)
        Sleep(800)

    } catch as e {
        LogVisibleNames()
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
