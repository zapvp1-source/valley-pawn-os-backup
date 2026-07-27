; ============================================================================
; reports/FpdLookback12Mo.ahk
;
; Runs the "Claude FPD 12-month Lookback" saved Ad Hoc loan report — same
; column shape as FpdCohort, but the saved-report criteria covers the last
; 365 days (Loan Date IN [today-365d .. today] AND Last Payment Date IS NULL)
; instead of the rolling 60-90-day cohort window.
;
; SKILL it powers: fpd-history-backfill (one-time) AND any future
; quarterly/monthly chronic-risk refresh.
;
; UI path: identical to FpdCohort — Loans/Buys -> Custom Reports ->
; Choose Saved Report -> "Claude FPD 12-month Lookback" -> Ok -> walk grid.
;
; Output CSV columns: whatever the saved Bravo report exposes. Same shape as
; FpdCohort assuming Joshua mirrors the columns when he creates the report
; (Ticket Number, Category, Full Description, Loan Amount).
;
; Prerequisite: Joshua creates the saved report "Claude FPD 12-month Lookback"
; in any one store (saved reports are company-wide). If the report doesn't
; exist, SelectSavedReport will fail and the cell will return an error.
; ============================================================================

#Requires AutoHotkey v2.0

global FPD12MO_ELEMENTS := Map(
    "sidebar_loans_buys",      "Loans/Buys",
    "panel_custom_reports",    "Custom Reports",
    "saved_report_combo",      "Choose Saved Report",
    "saved_report_value",      "Claude FPD 12-month Lookback",
    "dialog_ok",               "Ok",
    "panel_cancel",            "Cancel"
)

PullFpdLookback12Mo(store, date, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "fpd-lookback-12mo",
        "store",       store,
        "date",        date,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    outputPath := outputDir . "\" . OutputFilename(date, store, "fpd-lookback-12mo")
    LogMessage("[" . store . "] FpdLookback12Mo date=" . date . " -> " . outputPath)

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
    rowsWritten := 0

    try {
        DismissPopups()
        LogMessage("  step 1: open Loans/Buys")
        ClickByName(FPD12MO_ELEMENTS["sidebar_loans_buys"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: click Custom Reports")
        ClickByName(FPD12MO_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(1500)

        LogMessage("  step 3: select 'Claude FPD 12-month Lookback' saved report")
        SelectSavedReport(FPD12MO_ELEMENTS["saved_report_combo"], FPD12MO_ELEMENTS["saved_report_value"])

        LogMessage("  step 4: click Ok")
        ClickByName(FPD12MO_ELEMENTS["dialog_ok"], 5000)

        ; List renders. Title shows "Loans/Buys - Specific: NN" OR
        ; "Loans To Expire: 0" for empty result. Expect MUCH higher counts
        ; than the weekly cohort (potentially hundreds per store).
        Sleep(3000)
        DismissPopups()

        count := ParseCountFromTitle()
        LogMessage("    count from title: " . count)

        if (count = 0) {
            LogMessage("    [empty] count=0 — writing zero-row sentinel CSV")
            FileAppend("Ticket Number,Category,Full Description,Loan Amount`r`n", outputPath, "UTF-8-RAW")
            rowsWritten := 0
        } else {
            LogMessage("  step 5: wait for DataItems to render")
            gridReady := false
            rendCheckStart := A_TickCount
            Loop {
                try {
                    root := GetBravoRoot()
                    di := root.FindElements({Type: "DataItem"})
                    if (di && di.Length > 0) {
                        LogMessage("    [grid] rendered with " . di.Length . " initial DataItems after " . ((A_TickCount - rendCheckStart) // 1000) . "s")
                        gridReady := true
                        break
                    }
                }
                if (A_TickCount - rendCheckStart > 120000)
                    break
                Sleep(2000)
            }
            if (!gridReady) {
                LogVisibleNames()
                throw Error("FPD 12-month grid did not render within 120s after Ok click")
            }
            Sleep(1500)

            LogMessage("  step 6: walk grid and write row-level CSV")
            rowsWritten := WriteBuysGridToCsv(outputPath)
            if (rowsWritten < 0) {
                LogVisibleNames()
                throw Error("WriteBuysGridToCsv returned -1 (no rows / no columns captured)")
            }
            LogMessage("    wrote " . rowsWritten . " data rows to CSV")
        }

        ; Back to Dashboard
        try ClickByName(FPD12MO_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        try ClickByName(FPD12MO_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)

    } catch as e {
        LogVisibleNames()
        return Fail(result, started, "UIA click sequence failed: " . e.Message)
    }

    result["row_count"]   := rowsWritten
    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: count_from_title=" . count . " rows_written=" . rowsWritten . ", " . result["duration_ms"] . "ms")
    return result
}
