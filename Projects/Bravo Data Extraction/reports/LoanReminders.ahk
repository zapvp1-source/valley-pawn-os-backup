; ============================================================================
; reports/LoanReminders.ahk   (ADDITIVE - 2026-11-20)
;
; Pipeline cell: loan-reminders
;   Loans/Buys -> Custom Reports -> saved "Claude Loan Reminders" (created 2026-11-20: Ticket Kind = LOAN,
;   Due Date range, Shared Company-Wide) run with the "SHARED COMPANY-WIDE | FDP" layout, 5000-row cap.
;   Read only: runs the saved report and exports; nothing is saved or changed in Bravo.
;
; WHY: Joshua 11/19-11/20 - loan reminder texts move from Bravo ($0.07 each) to Chekkit. The sender needs every
; loan by due date with Disposition, Customer, MobilePawn and SMS columns, nightly, from a native agent.
;
; Trigger "date" token (no "|" allowed in host-queue jobs):
;   YYYY-MM-DD                 -> due dates from 45 days before to 6 days after that day (past-due texts repeat every Friday)
;                                 -> <that day>_<STORE>_loan-reminders.csv
;   YYYY-MM-DD..YYYY-MM-DD     -> exactly that due-date range -> <end>_<STORE>_loan-reminders.csv
; Reuses FwbRun (ForfeitureWinback.ahk) unchanged. Registered with two ADDED lines in bravo_watcher.ahk.
; ============================================================================
#Requires AutoHotkey v2.0

PullLoanReminders(store, dateOrRange, outputDir) {
    tok := Trim(dateOrRange)
    lay := "|rows=5000|layout=SHARED COMPANY-WIDE | FDP"
    if RegExMatch(tok, "^(\d{4})-(\d{2})-(\d{2})$", &m) {
        base := m[1] . m[2] . m[3] . "000000"
        d1 := FormatTime(DateAdd(base, -45, "Days"), "yyyy-MM-dd")
        d2 := FormatTime(DateAdd(base, 6, "Days"), "yyyy-MM-dd")
        opts := d1 . ".." . d2 . lay . "|stamp=" . tok
    } else if RegExMatch(tok, "^\d{4}-\d{2}-\d{2}\.\.\d{4}-\d{2}-\d{2}$") {
        opts := tok . lay
    } else {
        return Map("report", "loan-reminders", "store", store, "date", dateOrRange, "status", "error", "output_path", "", "row_count", 0, "duration_ms", 0, "error", "date must be YYYY-MM-DD or YYYY-MM-DD..YYYY-MM-DD")
    }
    res := FwbRun(store, opts, outputDir, "Loans/Buys", "Claude Loan Reminders", "loan-reminders")
    if (res["status"] != "success" && InStr(res["error"], "column layout")) {
        LogMessage("  [loan-reminders] layout pick failed - one retry")
        Sleep(5000)
        res := FwbRun(store, opts, outputDir, "Loans/Buys", "Claude Loan Reminders", "loan-reminders")
    }
    return res
}
