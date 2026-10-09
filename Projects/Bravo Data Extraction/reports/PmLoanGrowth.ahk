; ============================================================================
; reports/PmLoanGrowth.ahk   (ADDITIVE — 2026-10-07)
;
; Pipeline cell: pm-loan-growth
;   Loans/Buys -> Custom Reports -> an EXISTING saved report, run with the
;   existing "SHARED COMPANY-WIDE | FDP" column layout (Ticket, Category, Full
;   Description, Disposition, dates, Customer, Loan Amount, Age, MobilePawn,
;   SMS, Last Payment) and a 5000-row cap — this run only, nothing saved.
;
; WHY: Joshua 10/7 — grow loan balances on jewelry / precious-metal / coin
; loans that have had at least one paid extension (target up to 75% of melt).
; Needs every open loan with its category + payment history.
;
; Trigger "date" token picks the saved report (no "|" allowed in host-queue jobs):
;   walk    -> "Loan Walk"      (all open loans)        -> <stamp>_<STORE>_pm-loan-growth-walk.csv
;   jewelry -> "jewelry"        (company-wide saved)    -> <stamp>_<STORE>_pm-loan-growth-jewelry.csv
; Reuses FwbRun (ForfeitureWinback.ahk) unchanged. Nothing existing is modified.
; Registered with two ADDED lines in bravo_watcher.ahk.
; ============================================================================
#Requires AutoHotkey v2.0

PullPmLoanGrowth(store, dateOrRange, outputDir) {
    ; PAUSE SWITCH (2026-10-08): while  <project>\pm_loan_growth.PAUSED  exists, every pm-loan-growth
    ; cell returns an error immediately without touching Bravo (keeps the morning report window clear
    ; and drains stale queued jobs). Delete the file to resume. No watcher restart needed.
    if FileExist(A_ScriptDir . "\pm_loan_growth.PAUSED") {
        LogMessage("  [pm-loan-growth] PAUSED flag present - skipping " . store . " " . dateOrRange)
        return Map("report", "pm-loan-growth", "store", store, "date", dateOrRange, "status", "error", "output_path", "", "row_count", 0, "duration_ms", 0, "error", "paused")
    }
    ; tokens: walk (FDP layout) | walkdesc | walkplain | jewelry | byamount | portfolio  (probes, 10/7)
    ; PRODUCTION token:  p:YYYY-MM-DD..YYYY-MM-DD  -> saved "Claude Loan Portfolio 2026"
    ;   (Ticket Kind = LOAN, Create Date range overridden to the given range, every disposition)
    ;   with the FDP layout, 5000-row cap -> <end>_<STORE>_pm-loan-growth-p<YYYYMMDD start>.csv
    ;   The analysis keeps Disposition = ON LOAN.  Layout pick is flaky on some stores, so one retry.
    tok := Trim(dateOrRange)
    if RegExMatch(tok, "i)^p:(\d{4}-\d{2}-\d{2})\.\.(\d{4}-\d{2}-\d{2})$", &m) {
        opts := m[1] . ".." . m[2] . "|rows=5000|tag=p" . StrReplace(m[1], "-", "") . "|layout=SHARED COMPANY-WIDE | FDP"
        res := FwbRun(store, opts, outputDir, "Loans/Buys", "Claude Loan Portfolio 2026", "pm-loan-growth")
        if (res["status"] != "success" && InStr(res["error"], "column layout")) {
            LogMessage("  [pm-loan-growth] layout pick failed - one retry")
            Sleep(5000)
            res := FwbRun(store, opts, outputDir, "Loans/Buys", "Claude Loan Portfolio 2026", "pm-loan-growth")
        }
        return res
    }
    tok := StrLower(tok)
    rpt := (tok = "jewelry") ? "jewelry" : "Loan Walk"
    if (tok = "byamount")
        rpt := "Loans By Amount"
    else if (tok = "portfolio")
        rpt := "Claude Loan Portfolio 2026"
    lay := "|layout=SHARED COMPANY-WIDE | FDP"
    if (tok = "walkdesc")
        lay := "|layout=SHARED COMPANY-WIDE | Full description and cost"
    else if (tok = "walkplain")
        lay := ""
    tag := (tok = "jewelry" || tok = "walkdesc" || tok = "walkplain" || tok = "byamount" || tok = "portfolio") ? tok : "walk"
    return FwbRun(store, "saved|rows=5000|tag=" . tag . lay, outputDir, "Loans/Buys", rpt, "pm-loan-growth")
}
