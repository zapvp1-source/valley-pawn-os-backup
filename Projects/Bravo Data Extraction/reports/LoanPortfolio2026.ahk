; ============================================================================
; reports/LoanPortfolio2026.ahk
;
; Runs the "Claude Loan Portfolio 2026" saved Ad Hoc loan report for a single
; store across a configurable date range. Exports the full row detail as CSV.
;
; SKILL it powers: Optimize Loan Portfolio project — true-ROI analysis by
; collateral category. Distinct from LoanReviews.ahk (which uses the
; "Claude Loan Reviews" saved report). Cloned 2026-05-20 to keep the existing
; LoanReviews path UNTOUCHED while adding a portfolio-wide cohort dataset.
;
; Saved-report criteria (built in Bravo, shared company-wide as
; "Claude Loan Portfolio 2026"):
;   - Active Loans and Buys unchecked (historical + active)
;   - Ticket Kind = LOAN
;   - Pawn Date range [overridden at runtime via positions 1/2]
;   - Initial Rows = 5000+
;   - Sort By = Pawn Date, Ascending
;
; Display columns (in this order):
;   Ticket Number, Pawn Date, Disposition, Disposition Date, Category,
;   Full Description, Loan Amount
;
; UI path: Dashboard -> Loans/Buys -> Custom Reports -> Choose Saved Report
;   -> "Claude Loan Portfolio 2026" -> override Start/End Date -> Update -> Ok
;   -> grid
;
; Trigger schema (string in "date" field):
;   "YYYY-MM-DD"                       — single day
;   "YYYY-MM-DD..YYYY-MM-DD"           — explicit range
;
; Cloned from LoanReviews.ahk on 2026-05-20. The only differences are:
;   - saved_report_value          ("Claude Loan Portfolio 2026")
;   - output filename suffix      ("loan-portfolio-2026")
;   - function + constants names  (PullLoanPortfolio2026 / LOAN_PORTFOLIO_2026_ELEMENTS)
;   - report name in result map   ("loan-portfolio-2026")
;   - zero-row sentinel header    (includes Pawn Date, Disposition, Disposition Date)
; Everything else — navigation, date overrides, grid walking via the shared
; WriteBuysGridToCsv from BuysFromPublic.ahk — is identical.
; ============================================================================
#Requires AutoHotkey v2.0

global LOAN_PORTFOLIO_2026_ELEMENTS := Map(
    "sidebar_loans_buys",      "Loans/Buys",
    "panel_custom_reports",    "Custom Reports",
    "saved_report_combo",      "Choose Saved Report",
    "saved_report_value",      "Claude Loan Portfolio 2026",
    "dialog_ok",               "Ok",
    "panel_cancel",            "Cancel"
)

PullLoanPortfolio2026(store, dateOrRange, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "loan-portfolio-2026",
        "store",       store,
        "date",        dateOrRange,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    ; --- Parse date range ---------------------------------------------------
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
    LogMessage("[" . store . "] LoanPortfolio2026 startDate=" . startDate . " endDate=" . endDate)

    outputFileName := startDate . "_to_" . endDate . "_" . store . "_loan-portfolio-2026.csv"
    outputPath := outputDir . "\" . outputFileName
    LogMessage("  output -> " . outputPath)

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

    ; Pre-dismiss stuck dialogs (mirrors LowDollarLoans defensive cleanup;
    ; covers Bravo's btnCancel, PART_OkDialogButton, PART_CancelDialogButton).
    ActivateBravo()
    Loop 4 {
        dismissed := false
        try {
            root := GetBravoRoot()
            cancelEl := root.FindElement({AutomationId: "btnCancel"})
            if cancelEl {
                try {
                    cancelEl.InvokePattern.Invoke()
                    dismissed := true
                } catch as ie {
                    try {
                        cancelEl.Click("left")
                        dismissed := true
                    }
                }
                Sleep(900)
            }
        }
        try {
            root := GetBravoRoot()
            okEl := root.FindElement({AutomationId: "PART_OkDialogButton"})
            if okEl {
                try {
                    okEl.InvokePattern.Invoke()
                    dismissed := true
                    Sleep(900)
                }
            }
        }
        try {
            root := GetBravoRoot()
            cancelEl := root.FindElement({AutomationId: "PART_CancelDialogButton"})
            if cancelEl {
                try {
                    cancelEl.InvokePattern.Invoke()
                    dismissed := true
                    Sleep(900)
                }
            }
        }
        if (!dismissed)
            break
    }
    Sleep(300)

    if !BackToDashboard()
        return Fail(result, started, "BackToDashboard could not return Bravo to Dashboard")
    Sleep(500)
    DismissPopups()

    count := 0
    rowsWritten := 0

    try {
        DismissPopups()

        LogMessage("  step 1: open Loans/Buys")
        ClickByName(LOAN_PORTFOLIO_2026_ELEMENTS["sidebar_loans_buys"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: click Custom Reports")
        ClickByName(LOAN_PORTFOLIO_2026_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(1500)

        LogMessage("  step 3: select 'Claude Loan Portfolio 2026' saved report")
        SelectSavedReport(LOAN_PORTFOLIO_2026_ELEMENTS["saved_report_combo"], LOAN_PORTFOLIO_2026_ELEMENTS["saved_report_value"])
        Sleep(1000)

        ; Date override via ValuePattern (works for any saved report
        ; that exposes Create Date as the first/second date wrapper).
        ; Pattern: SetReportDate -> SetReportDate -> Update (long wait) ->
        ; ClickByName(Ok). Longer post-Update sleep gives Bravo time to
        ; re-enable the Ok button after the criteria object commits.
        LogMessage("  step 4a: override Start Date via ValuePattern -> " . startDate)
        try {
            SetReportDate(1, startDate)
            Sleep(600)
        } catch as e {
            LogMessage("    WARN: SetReportDate(1) failed: " . e.Message)
        }

        LogMessage("  step 4b: override End Date via ValuePattern -> " . endDate)
        try {
            SetReportDate(2, endDate)
            Sleep(600)
        } catch as e {
            LogMessage("    WARN: SetReportDate(2) failed: " . e.Message)
        }

        LogMessage("  step 5: click Update to commit modified criteria")
        try {
            ClickByName("Update", 4000)
            LogMessage("    [UIA] clicked Update")
        } catch as e {
            LogMessage("    WARN: Update click failed: " . e.Message)
        }

        ; Long wait for Bravo to process Update and re-enable Ok.
        Sleep(4000)
        ActivateBravo()
        Sleep(500)

        LogMessage("  step 6: click Ok (after Update; longer wait)")
        try {
            ClickByName(LOAN_PORTFOLIO_2026_ELEMENTS["dialog_ok"], 6000)
            LogMessage("    [UIA] clicked Ok")
        } catch as e {
            LogMessage("    WARN: Ok click failed: " . e.Message . " -- trying Enter")
            Send("{Enter}")
        }
        Sleep(3000)
        DismissPopups()

        LogMessage("  step 6b: waiting for DataItem rows to render")
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

        count := ParseCountFromTitle()
        LogMessage("    count from title: " . count)

        if (count = 0 && !gridReady) {
            LogMessage("    [empty] count=0 — writing zero-row sentinel CSV")
            FileAppend("Ticket Number,Pawn Date,Disposition,Disposition Date,Category,Full Description,Loan Amount`r`n", outputPath, "UTF-8-RAW")
            rowsWritten := 0
        } else {
            if (!gridReady) {
                LogVisibleNames()
                throw Error("Loan portfolio grid did not render within 120s after Ok click")
            }
            Sleep(1500)
            LogMessage("  step 7: walk grid and write row-level CSV")
            rowsWritten := WriteBuysGridToCsv(outputPath)
            if (rowsWritten < 0) {
                LogVisibleNames()
                throw Error("WriteBuysGridToCsv returned -1 (no rows / no columns captured)")
            }
            LogMessage("    wrote " . rowsWritten . " data rows to CSV")
        }

        try ClickByName(LOAN_PORTFOLIO_2026_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        try ClickByName(LOAN_PORTFOLIO_2026_ELEMENTS["panel_cancel"], 3000)
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
