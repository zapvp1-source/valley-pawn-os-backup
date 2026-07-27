; ============================================================================
; reports/FpdCohort.ahk
;
; Runs the "Claude First Payment Default" saved Ad Hoc loan report for a
; single store and dumps the FULL grid — one CSV row per defaulted loan —
; so the consumer (weekly-fpd-ranking skill) can compute per-store ranking
; AND category/item breakdowns from the same source.
;
; SKILL it powers: weekly-fpd-ranking
;
; UI path:
;   Dashboard -> Loans/Buys (sidebar)
;   -> right panel "Pick Up" -> Custom Reports
;   -> Bravo Custom Loan Report Generator dialog
;       -> Choose Saved Report -> "Claude First Payment Default" (SHARED COMPANY-WIDE)
;       -> Ok
;   -> List renders; title bar shows "Loans/Buys - Specific: NN" (count)
;   -> Walk grid via UIA, write one row per defaulted loan
;   -> Cancel back to Dashboard
;
; The saved report itself encodes the FPD cohort criteria (Loan Date in the
; rolling 60-90-day window, Last Payment Date IS NULL). The watcher does NOT
; build criteria here; it just runs the saved report.
;
; Output CSV columns: whatever the saved Bravo report exposes. With the current
; "Claude First Payment Default" report shape that's:
;   Ticket Number, Category, Full Description, Loan Amount
; (matches BuysFromPublic — both are Loans/Buys grids.)
;
; If the saved report is empty for a store (count=0), the CSV is written with
; ONLY a sentinel header row "store,date,count,dollar_sum" + a single zero
; row, preserving backward compatibility with any consumer that still expects
; the old aggregate shape for empty cells.
;
; 2026-05-18 — Rewritten to dump full grid instead of count+sum aggregate.
;              Previous aggregate version backed up as FpdCohort.ahk.bak-pre-rowlevel-2026-05-18.
; ============================================================================

#Requires AutoHotkey v2.0

global FPD_ELEMENTS := Map(
    "sidebar_loans_buys",      "Loans/Buys",
    "panel_custom_reports",    "Custom Reports",
    "saved_report_combo",      "Choose Saved Report",
    "saved_report_value",      "Claude First Payment Default",
    "dialog_ok",               "Ok",
    "panel_cancel",            "Cancel"
)

PullFpdCohort(store, date, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "fpd-cohort",
        "store",       store,
        "date",        date,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    outputPath := outputDir . "\" . OutputFilename(date, store, "fpd-cohort")
    LogMessage("[" . store . "] FpdCohort date=" . date . " -> " . outputPath)

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
        ClickByName(FPD_ELEMENTS["sidebar_loans_buys"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: click Custom Reports")
        ClickByName(FPD_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(1500)

        LogMessage("  step 3: select 'Claude First Payment Default' saved report")
        SelectSavedReport(FPD_ELEMENTS["saved_report_combo"], FPD_ELEMENTS["saved_report_value"])

        LogMessage("  step 4: click Ok")
        ClickByName(FPD_ELEMENTS["dialog_ok"], 5000)

        ; List renders. Title shows "Loans/Buys - Specific: NN" OR
        ; "Loans To Expire: 0" for empty result.
        Sleep(3000)
        DismissPopups()

        count := ParseCountFromTitle()
        LogMessage("    count from title: " . count)

        if (count = 0) {
            ; Empty cohort — write a sentinel CSV so consumers know the cell
            ; ran successfully but had no defaulted loans.
            LogMessage("    [empty] count=0 — writing zero-row sentinel CSV")
            FileAppend("Ticket Number,Category,Full Description,Loan Amount`r`n", outputPath, "UTF-8-RAW")
            rowsWritten := 0
        } else {
            ; Count > 0 — wait for grid to settle, then walk it.
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
                if (A_TickCount - rendCheckStart > 60000)
                    break
                Sleep(1500)
            }
            if (!gridReady) {
                LogVisibleNames()
                throw Error("FPD grid did not render within 60s after Ok click")
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
        try ClickByName(FPD_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        try ClickByName(FPD_ELEMENTS["panel_cancel"], 3000)
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
