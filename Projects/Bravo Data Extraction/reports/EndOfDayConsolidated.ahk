; ============================================================================
; reports/EndOfDayConsolidated.ahk
;
; Pulls Bravo's "End of Day - Consolidated" report and exports it as CSV.
; This is a BUILT-IN Bravo report (not a saved Ad Hoc), accessed via:
;   Dashboard -> Reports (sidebar)
;   -> Closing Reports section -> End of Day - Consolidated (tile)
;   -> Date config dialog -> set Date -> Ok
;   -> Report Preview renders
;   -> Export Document -> Csv -> save path -> OK
;   -> Done x2 back to Dashboard
;
; CONSOLIDATED — produces cross-store totals in a single CSV. We still pass
; a `store` arg (the handler runs from whatever store the watcher is on),
; but the CSV content is company-wide. The store appears in the filename
; for traceability ("which store's session produced this run").
;
; Cloned from EndOfMonth.ahk. Differences:
;   - tile name "End of Day - Consolidated" instead of "End of Month"
;   - report has a SINGLE date (no range)
;   - no SetReportDate(2) call
;   - parent section is "Closing Reports" (same as EOM)
;
; Trigger schema:
;   "stores": ["CUL"]                  ; any one store — output is cross-store
;   "date":   "YYYY-MM-DD"             ; single date
;
; Output filename: <DATE>_<STORE>_end-of-day-consolidated.csv
; ============================================================================

#Requires AutoHotkey v2.0

global EOD_CONS_ELEMENTS := Map(
    "sidebar_reports",    "Reports",
    "report_tile",        "End of Day - Consolidated",
    "config_ok",          "Ok",
    "preview_export",     "Export...",
    "export_ok",          "OK",
    "panel_done",         "Done"
)

PullEndOfDayConsolidated(store, dateIso, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "end-of-day-consolidated",
        "store",       store,
        "date",        dateIso,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    ; --- Parse date ---------------------------------------------------------
    ; EOD Consolidated takes a SINGLE date, not a range. If a range was
    ; passed in (e.g. "2026-05-27..2026-05-27"), use the start date.
    if InStr(dateIso, "..") {
        parts := StrSplit(dateIso, "..")
        dateIso := Trim(parts[1])
    }
    LogMessage("[" . store . "] EndOfDayConsolidated date=" . dateIso)

    outputPath := outputDir . "\" . OutputFilename(dateIso, store, "end-of-day-consolidated")
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
        ClickByName(EOD_CONS_ELEMENTS["sidebar_reports"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: double-click End of Day - Consolidated tile (= Preview)")
        DoubleClickByName(EOD_CONS_ELEMENTS["report_tile"], 8000)
        Sleep(2500)
        DismissPopups()

        ; --- Single-date dialog -----------------------------------------
        ; EOD Consolidated has ONE date field. Use SetReportDate(1) only.
        LogMessage("  step 3: try SetReportDate(1, " . dateIso . ")")
        try {
            SetReportDate(1, dateIso)
            Sleep(600)
        } catch as e {
            LogMessage("    WARN: SetReportDate(1) failed: " . e.Message)
        }

        ; Push focus off the date control so Bravo commits/validates
        ; and re-enables the dialog Ok button.
        Send("{Tab}")
        Sleep(800)
        ActivateBravo()
        Sleep(500)

        LogMessage("  step 4: submit dialog (Enter primary, ClickByName Ok fallback)")
        Send("{Enter}")
        LogMessage("    [key] {Enter} sent as primary submit")
        Sleep(1500)

        if !FindByName(EOD_CONS_ELEMENTS["preview_export"], 0) {
            LogMessage("    [fallback] Preview not yet visible, trying ClickByName(Ok)")
            try {
                ClickByName(EOD_CONS_ELEMENTS["config_ok"], 5000)
                LogMessage("    [UIA] clicked Ok (fallback)")
            } catch as e {
                LogMessage("    WARN: Ok click fallback failed: " . e.Message)
            }
            Sleep(1500)
        }

        ; Closing reports can take a while to render — give Preview up to 60s.
        if !FindByName(EOD_CONS_ELEMENTS["preview_export"], 60000)
            throw Error("Preview did not render within 60s (Export Document button never appeared)")
        Sleep(800)

        ; --- Step 4b: turn off Continuous Scrolling (added 2026-05-29) -----
        ; Bravo's Report Preview has an "Enable Continuous Scrolling" toggle
        ; that, when pressed, forces the entire report to render as one giant
        ; canvas. For wide multi-column reports, this freezes Bravo for 3+
        ; minutes; the Export OK click then lands on a still-rendering UI
        ; and the CSV never gets written. Joshua confirmed the toggle re-
        ; enables itself on every Bravo restart — so this check must run on
        ; every cell, not just once per session. Wrapped so it can't itself
        ; throw and mask the original error.
        try {
            csButton := FindByName("Enable Continuous Scrolling", 1000)
            if (csButton) {
                state := 0
                try state := csButton.TogglePattern.CurrentToggleState
                if (state = 1) {  ; UIA.ToggleState.On
                    LogMessage("    [pre-export] Continuous Scrolling is ON — calling Toggle() to flip state")
                    ; Use TogglePattern.Toggle() directly — Click("left") was a physical mouse
                    ; click at element center which often didn't actually toggle the CheckBox
                    ; in Bravo's WPF preview ribbon. v5 smoke (2026-05-29) confirmed: DPO worked
                    ; by coincidence (small report renders fast even with CS on); EOM hung 3min
                    ; because CS was still actually ON.
                    try csButton.TogglePattern.Toggle()
                    Sleep(2500)
                    ; verify the toggle actually flipped — if still on, try once more
                    newState := state
                    try newState := csButton.TogglePattern.CurrentToggleState
                    if (newState = 1) {
                        LogMessage("    [pre-export] WARN: first Toggle() didn't flip; retrying via Click()")
                        try csButton.Click("left")
                        Sleep(2500)
                        try newState := csButton.TogglePattern.CurrentToggleState
                    }
                    LogMessage("    [pre-export] post-toggle state = " . newState . " (0=Off)")
                    Sleep(3000)  ; give Bravo time to re-paginate after toggle
                } else {
                    LogMessage("    [pre-export] Continuous Scrolling already OFF (state=" . state . ")")
                }
            } else {
                LogMessage("    [pre-export] Continuous Scrolling button not found — skipping")
            }
        } catch as e {
            LogMessage("    [pre-export] WARN: Continuous Scrolling toggle-off failed: " . e.Message)
        }

        LogMessage("  step 5: click Export Document")
        ClickByName(EOD_CONS_ELEMENTS["preview_export"], 5000)
        if !FindByName(EOD_CONS_ELEMENTS["export_ok"], 8000)
            throw Error("Export Document dialog did not appear within 8s")

        Sleep(800)
        LogMessage("  step 6: set Export format = Csv")
        SetExportFormatCsv()

        LogMessage("  step 7: set File path = " . outputPath)
        SetExportFilePath(outputPath)

        LogMessage("  step 8: uncheck open-after-export")
        UncheckOpenAfterExport()

        LogMessage("  step 9: click export OK")
        ClickByName(EOD_CONS_ELEMENTS["export_ok"], 5000)

        ; Wait for CSV — closing reports can be slow on cold runs.
        if !WaitForFile(outputPath, 180)
            throw Error("CSV file did not appear at " . outputPath . " within 180s")
        Sleep(2000)  ; let Bravo finish writing before size check

        ; Reject empty/partial exports.
        sz := 0
        try sz := FileGetSize(outputPath)
        if (sz < 200) {
            throw Error("Exported CSV is too small (" . sz . " bytes) — Bravo export likely failed mid-write. Path: " . outputPath)
        }
        LogMessage("  step 9b: CSV size check passed (" . sz . " bytes)")

        ; --- Robust exit sequence -----------------------------------------
        LogMessage("  step 10: robust exit (Esc, Done x N, BackToDashboard)")
        try ActivateBravo()
        Sleep(400)
        Send("{Escape}")
        Sleep(800)
        Loop 3 {
            if ExistsByName("Reports")
                break
            try ClickByName(EOD_CONS_ELEMENTS["panel_done"], 3000)
            Sleep(1200)
            DismissPopups()
        }
        if !ExistsByName("Reports") {
            LogMessage("  step 10b: BackToDashboard fallback")
            BackToDashboard(8)
        }
        Sleep(500)
        DismissPopups()

    } catch as e {
        LogVisibleNames()
        ; --- Cascade-safe error recovery (added 2026-05-29) ----------------
        ; A bare Fail() leaves Bravo on whatever screen it was on at the throw
        ; point. If that's Report Preview, every subsequent cell's EnsureStore/
        ; BackToDashboard cascades and fails. Best-effort exit before bailing.
        ; Wrapped so recovery can't itself throw and mask the original error.
        try {
            LogMessage("    [recovery] attempting best-effort exit to Dashboard")
            try ActivateBravo()
            Sleep(400)
            try Send("{Escape}")
            Sleep(800)
            Loop 3 {
                onReports := false
                try onReports := ExistsByName("Reports")
                if onReports
                    break
                try ClickByName("Done", 2000)
                Sleep(1000)
                try DismissPopups()
            }
            onReports := false
            try onReports := ExistsByName("Reports")
            if !onReports {
                LogMessage("    [recovery] BackToDashboard fallback")
                try BackToDashboard(8)
            }
            Sleep(500)
            try DismissPopups()
        }
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
