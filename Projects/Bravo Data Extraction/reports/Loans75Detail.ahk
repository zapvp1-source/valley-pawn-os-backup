; ============================================================================
; reports/Loans75Detail.ahk   (ADDITIVE — 2026-09-30)
;
; Pipeline cell: loans75-detail
;   Loans/Buys -> Custom Reports -> saved "75 Days Past Due" (the same saved
;   report the weekly loans-75-days-past-due cell runs) -> FULL row capture.
;
; WHY: the existing loans-75-days-past-due cell reads count + Sum only, and its
; count comes from the rendered DataItem rows (virtualized, ~22 max), so stores
; with more than ~22 past-due loans report exactly 22. loans75-gridread has the
; same single-pass read. Neither gives the per-loan / per-customer list needed
; for the October 2026 75-day rule-change outreach (email / text / push).
;
; HOW: reuses FwbRun (ForfeitureWinback.ahk) unchanged — the proven generic
; saved-report runner with the full-capture grid walker (FwbWriteGrid) and the
; .meta expected/captured sidecar. Trigger "date" is normally "saved" (run the
; saved criteria unchanged); "|rows=N" / "|layout=..." / "|stamp=YYYY-MM-DD"
; options work exactly as documented in ForfeitureWinback.ahk.
;
; Output: <stamp>_<STORE>_loans75-detail.csv (+ .meta)
; Columns come from the saved report's column layout (as of 2026-06-17:
; Ticket Number, Disposition, Disposition Date, Due Date, Pull Date, Customer,
; Loan Amount, Age, MobilePawn, SMS).
;
; NOTHING existing is modified. Registered in bravo_watcher.ahk with two ADDED
; lines (#Include + REPORT_HANDLERS["loans75-detail"]).
; ============================================================================
#Requires AutoHotkey v2.0

PullLoans75Detail(store, dateOrRange, outputDir) {
    return FwbRun(store, dateOrRange, outputDir, "Loans/Buys", "75 Days Past Due", "loans75-detail")
}
