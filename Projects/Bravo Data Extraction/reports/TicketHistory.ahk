; ============================================================================
; reports/TicketHistory.ahk   (ADDITIVE - 2026-11-27, Bravo Warehouse: Joshua "we need ALL the data")
;
; Pipeline cells: loans-written, buys-written
;   Loans/Buys -> Custom Reports -> existing saved reports, run with the "SHARED COMPANY-WIDE | FDP" layout
;   (Ticket Number, Category, Full Description, Disposition, Disposition Date, Due Date, Pull Date, Customer,
;   Loan Amount, Age, MobilePawn, SMS, Last Payment), 5000-row cap.
;     loans-written -> "Claude Loan Portfolio 2026" (Ticket Kind = LOAN, Create Date range, every disposition)
;     buys-written  -> "Claude Buy Reviews"        (buy tickets, date range)
;   Read only: runs the saved report and exports; nothing is saved or changed in Bravo.
;
; Trigger "date": YYYY-MM-DD..YYYY-MM-DD (required) -> <end>_<STORE>_<cell>.csv (+ .meta from FwbRun).
; Keep windows to one month per store. Reuses FwbRun (ForfeitureWinback.ahk) unchanged.
; Registered with ADDED lines in bravo_watcher.ahk.
; ============================================================================
#Requires AutoHotkey v2.0

ThRun(store, dateOrRange, outputDir, reportName, slug) {
    tok := Trim(dateOrRange)
    if !RegExMatch(tok, "^\d{4}-\d{2}-\d{2}\.\.\d{4}-\d{2}-\d{2}$")
        return Map("report", slug, "store", store, "date", dateOrRange, "status", "error", "output_path", "", "row_count", 0, "duration_ms", 0, "error", "date must be YYYY-MM-DD..YYYY-MM-DD")
    opts := tok . "|rows=5000|layout=SHARED COMPANY-WIDE | FDP"
    res := FwbRun(store, opts, outputDir, "Loans/Buys", reportName, slug)
    if (res["status"] != "success" && InStr(res["error"], "column layout")) {
        LogMessage("  [" . slug . "] layout pick failed - one retry")
        Sleep(5000)
        res := FwbRun(store, opts, outputDir, "Loans/Buys", reportName, slug)
    }
    if (res["status"] = "success" && res["row_count"] >= 5000) {
        res["status"] := "error"
        res["error"] := "5000 rows returned - at the row cap, use a shorter window"
    }
    return res
}

PullLoansWritten(store, dateOrRange, outputDir) {
    return ThRun(store, dateOrRange, outputDir, "Claude Loan Portfolio 2026", "loans-written")
}

PullBuysWritten(store, dateOrRange, outputDir) {
    return ThRun(store, dateOrRange, outputDir, "Claude Buy Reviews", "buys-written")
}
