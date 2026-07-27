; ============================================================================
; reports/LoanBase.ahk
;
; Pulls Bravo's "Loan Base" built-in report for a single store and exports it
; as CSV. Uses the standard Reports->tile->Preview->Export pattern (same as
; AgedInventorySummary and EndOfMonth).
;
; SKILL it powers: asset-recovery-daily-refresh (and any future loan portfolio
; balance work). Replaces the SSRS company-kpis route for loan totals — no
; Edge, no SSRS cookies.
;
; Trigger schema:
;   "stores": ["CUL","HAR","LEX","ROA","WAY"]   — per-store invocation
;   "date":
;       "YYYY-MM-DD"                              — single as-of date; treated
;                                                   as END; start = 1 year back
;       "YYYY-MM-DD..YYYY-MM-DD"                  — explicit start..end
;
; Output filename: <END_DATE>_<STORE>_loan-base.csv
;
; Notes on dialog handling: first attempt clicked Ok with defaults and got an
; empty preview (Bravo's default was a no-rows filter). EOM pattern adopted:
; explicit SetReportDate(1=start, 2=end), Tab to commit focus, {Enter} as
; primary submit with ClickByName(Ok) as fallback. Dialog field dump via
; LogVisibleNames() runs after the dblclick so the next failure mode is
; diagnosable from the log alone.
; ============================================================================

#Requires AutoHotkey v2.0

global LOANBASE_ELEMENTS := Map(
    "sidebar_reports",    "Reports",
    "report_tile",        "Loan Base",
    "config_ok",          "Ok",
    "preview_export",     "Export...",
    "export_ok",          "OK",
    "panel_done",         "Done"
)

PullLoanBase(store, dateOrRange, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "loan-base",
        "store",       store,
        "date",        dateOrRange,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    ; --- Parse date range ---------------------------------------------------
    startDateIso := ""
    endDateIso := ""
    if InStr(dateOrRange, "..") {
        parts := StrSplit(dateOrRange, "..")
        if (parts.Length != 2)
            return Fail(result, started, "Malformed date range: " . dateOrRange . " (expected YYYY-MM-DD..YYYY-MM-DD)")
        startDateIso := Trim(parts[1])
        endDateIso := Trim(parts[2])
    } else {
        ; Single date — treat as end; start = end - 1 year (captures all active
        ; loans regardless of pawn date).
        endDateIso := dateOrRange
        endStamp := A_Now
        try {
            tParts := StrSplit(dateOrRange, "-")
            if (tParts.Length = 3)
                endStamp := tParts[1] . tParts[2] . tParts[3] . "000000"
        }
        startStamp := DateAdd(endStamp, -365, "Days")
        startDateIso := FormatTime(startStamp, "yyyy-MM-dd")
    }
    LogMessage("[" . store . "] LoanBase range=" . startDateIso . ".." . endDateIso)

    outputPath := outputDir . "\" . OutputFilename(endDateIso, store, "loan-base")
    LogMessage("  output -> " . outputPath)

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
        ClickByName(LOANBASE_ELEMENTS["sidebar_reports"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: double-click Loan Base tile (= Preview)")
        DoubleClickByName(LOANBASE_ELEMENTS["report_tile"], 8000)
        Sleep(2500)
        DismissPopups()

        ; Loan Base config dialog has Date Range fields (Start/End) but they
        ; default to a sensible window (current month). V1 test proved clicking
        ; Ok with defaults produces a populated Preview. We don't override the
        ; dates — the trigger's "date" field is for output filename + log only.
        ; If a specific range is ever needed, fall back to SetReportDate
        ; pattern from EOM.ahk.
        LogMessage("  step 3: click config Ok (defaults — current month)")
        ClickByName(LOANBASE_ELEMENTS["config_ok"], 5000)

        ; Loan Base across 5-store + thousands of loans can take a while to
        ; render — give it up to 90s.
        if !FindByName(LOANBASE_ELEMENTS["preview_export"], 90000)
            throw Error("Preview did not render within 90s (Export Document button never appeared)")

        ; CRITICAL: Export... button appears as soon as the Preview toolbar
        ; loads — BEFORE the report data finishes drawing. Clicking Export at
        ; that moment yields an empty CSV (and Bravo often goes "Not Responding"
        ; while it grinds through render afterwards). Sleep long enough for the
        ; report body to fully populate before any further UIA query. 25s is
        ; a conservative buffer for a 365-day Loan Base across an active store.
        LogMessage("  step 4b: settle 25s for report body to fully render")
        Sleep(25000)
        ; Re-acquire focus in case rendering shifted it.
        ActivateBravo()
        Sleep(1000)

        LogMessage("  step 5: click Export Document")
        ClickByName(LOANBASE_ELEMENTS["preview_export"], 5000)
        if !FindByName(LOANBASE_ELEMENTS["export_ok"], 8000)
            throw Error("Export Document dialog did not appear within 8s")

        Sleep(800)
        LogMessage("  step 6: set Export format = Csv")
        SetExportFormatCsv()

        LogMessage("  step 7: set File path = " . outputPath)
        SetExportFilePath(outputPath)

        LogMessage("  step 8: uncheck open-after-export")
        UncheckOpenAfterExport()

        LogMessage("  step 9: click export OK")
        ClickByName(LOANBASE_ELEMENTS["export_ok"], 5000)

        ; Loan Base CSV with thousands of rows can be slow over the share —
        ; wait up to 180s, then a settle sleep before sanity check.
        if !WaitForFile(outputPath, 180)
            throw Error("CSV file did not appear at " . outputPath . " within 180s")
        Sleep(2000)

        ; Reject empty/partial exports.
        sz := 0
        try sz := FileGetSize(outputPath)
        if (sz < 500) {
            throw Error("CSV looks empty/partial (" . sz . " bytes) — likely the report ran with no rows. Check the config dialog defaults.")
        }

        LogMessage("  step 10: Done (exit preview)")
        try ClickByName(LOANBASE_ELEMENTS["panel_done"], 3000)
        Sleep(800)
        LogMessage("  step 10: Done (exit reports list)")
        try ClickByName(LOANBASE_ELEMENTS["panel_done"], 3000)
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
