; ============================================================================
; reports/SalesByVendor.ahk
;
; Pulls Bravo's Sales Report filtered to a date range and (optionally) a
; vendor / department set, exports as CSV. Powers the New Inventory Weekly
; Report by giving it last week's sales data per store.
;
; SKILL it powers: new-inv-weekly-report
;
; UI path:
;   Dashboard -> Reports (sidebar)
;   -> under Sales Reports -> Sales Report (or "Sales by Vendor" if available)
;   -> Preview
;   -> Sales Report Configuration dialog: Start Date, End Date, Vendor filter
;   -> Ok
;   -> Report Preview renders
;   -> Export... -> Csv -> path -> uncheck open-after -> OK
;   -> Done x2 back to Dashboard
;
; NOTE: The exact name of the sales tile and the filter dialog fields varies
; by Bravo version. This module's element names are best guesses from the SKILL
; docs; first run's diagnostic dump will reveal what's actually exposed.
; ============================================================================

#Requires AutoHotkey v2.0

global SBV_ELEMENTS := Map(
    "sidebar_reports",   "Reports",
    "report_tile",       "Sold Inventory",
    "config_ok",         "Ok",
    "preview_export",    "Export...",
    "export_ok",         "OK",
    "panel_done",        "Done"
)

PullSalesByVendor(store, date, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "sales-by-vendor",
        "store",       store,
        "date",        date,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    outputPath := outputDir . "\" . OutputFilename(date, store, "sales-by-vendor")
    LogMessage("[" . store . "] SalesByVendor start=" . date . " -> " . outputPath)

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
        return Fail(result, started, "BackToDashboard failed")
    Sleep(500)
    DismissPopups()

    try {
        LogMessage("  step 1: open Reports")
        ClickByName(SBV_ELEMENTS["sidebar_reports"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: double-click Sales Report tile")
        DoubleClickByName(SBV_ELEMENTS["report_tile"], 8000)
        Sleep(2500)
        DismissPopups()

        ; Set Start Date. End Date stays at today (default).
        LogMessage("  step 3: set Start Date")
        SetReportDate(SBV_ELEMENTS["config_start_date"], date)

        LogMessage("  step 4: click config Ok")
        ClickByName(SBV_ELEMENTS["config_ok"], 5000)

        if !FindByName(SBV_ELEMENTS["preview_export"], 30000)
            throw Error("Preview did not render within 30s")
        Sleep(500)

        LogMessage("  step 5: click Export Document")
        ClickByName(SBV_ELEMENTS["preview_export"], 5000)
        if !FindByName(SBV_ELEMENTS["export_ok"], 8000)
            throw Error("Export Document dialog did not appear within 8s")

        Sleep(800)
        SetExportFormatCsv()
        SetExportFilePath(outputPath)
        UncheckOpenAfterExport()
        ClickByName(SBV_ELEMENTS["export_ok"], 5000)

        if !WaitForFile(outputPath, 30)
            throw Error("CSV did not appear within 30s")
        Sleep(500)

        try ClickByName(SBV_ELEMENTS["panel_done"], 3000)
        Sleep(800)
        try ClickByName(SBV_ELEMENTS["panel_done"], 3000)
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
