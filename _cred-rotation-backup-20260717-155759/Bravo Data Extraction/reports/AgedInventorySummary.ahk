; ============================================================================
; reports/AgedInventorySummary.ahk
;
; Pulls Bravo's "Aged Inventory Summary" report for a single store and exports
; it as CSV. Defaults work for date (the report only has a single Date field
; that defaults to today). Same Export Document dialog as SRJ.
;
; SKILL it powers: weekly-aged-inventory-report
;
; UI path:
;   Dashboard -> Reports (sidebar)
;   -> Inventory Reports -> Aged Inventory Summary (tile)
;   -> Preview (right panel) [or double-click the tile]
;   -> Aged Inventory Summary Report Configuration dialog -> Ok (default date)
;   -> Report Preview renders
;   -> Export... -> set Csv + path -> uncheck open-after -> OK
;   -> Done x2 back to Dashboard
; ============================================================================

#Requires AutoHotkey v2.0

global AGEDINV_ELEMENTS := Map(
    "sidebar_reports",    "Reports",
    "report_tile",        "Aged Inventory Summary",
    "config_ok",          "Ok",
    "preview_export",     "Export...",
    "export_ok",          "OK",
    "panel_done",         "Done"
)

PullAgedInventorySummary(store, date, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "aged-inventory-summary",
        "store",       store,
        "date",        date,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    outputPath := outputDir . "\" . OutputFilename(date, store, "aged-inventory-summary")
    LogMessage("[" . store . "] AgedInventorySummary date=" . date . " -> " . outputPath)

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
        ClickByName(AGEDINV_ELEMENTS["sidebar_reports"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: double-click Aged Inventory Summary tile (= Preview)")
        DoubleClickByName(AGEDINV_ELEMENTS["report_tile"], 8000)
        Sleep(2500)
        DismissPopups()

        ; Aged Inventory Summary config dialog has only Date (defaults to today)
        ; - just click Ok.
        LogMessage("  step 3: click config Ok (defaults)")
        ClickByName(AGEDINV_ELEMENTS["config_ok"], 5000)

        if !FindByName(AGEDINV_ELEMENTS["preview_export"], 30000)
            throw Error("Preview did not render within 30s (Export Document button never appeared)")
        Sleep(500)

        LogMessage("  step 4: click Export Document")
        ClickByName(AGEDINV_ELEMENTS["preview_export"], 5000)
        if !FindByName(AGEDINV_ELEMENTS["export_ok"], 8000)
            throw Error("Export Document dialog did not appear within 8s")

        Sleep(800)
        LogMessage("  step 5: set Export format = Csv")
        SetExportFormatCsv()

        LogMessage("  step 6: set File path = " . outputPath)
        SetExportFilePath(outputPath)

        LogMessage("  step 7: uncheck open-after-export")
        UncheckOpenAfterExport()

        LogMessage("  step 8: click export OK")
        ClickByName(AGEDINV_ELEMENTS["export_ok"], 5000)

        if !WaitForFile(outputPath, 30)
            throw Error("CSV file did not appear at " . outputPath . " within 30s")
        Sleep(500)

        LogMessage("  step 9: Done (exit preview)")
        try ClickByName(AGEDINV_ELEMENTS["panel_done"], 3000)
        Sleep(800)
        LogMessage("  step 9: Done (exit reports list)")
        try ClickByName(AGEDINV_ELEMENTS["panel_done"], 3000)
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
