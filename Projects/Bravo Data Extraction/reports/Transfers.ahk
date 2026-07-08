; ============================================================================
; reports/Transfers.ahk
;
; Pulls Bravo's "Transfers" report and exports it as CSV.
; Built-in Bravo report (Closing Reports section).
; Date dialog shape TBD; handler handles both single and range gracefully.
;
; Cloned from EndOfMonth.ahk.
; ============================================================================

#Requires AutoHotkey v2.0

; ----------------------------------------------------------------------------
; ClampTransfersEndDate(yyyymmdd)
; Bravo's End of Month report calendar refuses today and future dates — Ok
; stays disabled if the bound DatePicker value is >= today. ValuePattern can
; paint the inner Edit's text, but the underlying control rejects the commit
; on Ok-click. Workaround: if the requested end date is today or later, clamp
; it to yesterday. Logged so the caller knows.
; ----------------------------------------------------------------------------
ClampTransfersEndDate(yyyymmdd) {
    parts := StrSplit(yyyymmdd, "-")
    if (parts.Length != 3)
        return yyyymmdd  ; malformed — let SetReportDate complain
    reqStamp  := parts[1] . parts[2] . parts[3]
    todayStmp := FormatTime(A_Now, "yyyyMMdd")
    if (reqStamp < todayStmp)
        return yyyymmdd  ; already in the past — leave alone
    ; Yesterday in YYYY-MM-DD
    yest := A_Now
    yest := DateAdd(yest, -1, "Days")
    return FormatTime(yest, "yyyy-MM-dd")
}


global T_ELEMENTS := Map(
    "sidebar_reports",    "Reports",
    "report_tile",        "Transfers",
    "config_ok",          "Ok",
    "preview_export",     "Export...",
    "export_ok",          "OK",
    "panel_done",         "Done"
)

PullTransfers(store, dateOrRange, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "transfers",
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
        ; Single date — treat as both start and end (one-day report)
        startDateIso := dateOrRange
        endDateIso := dateOrRange
    }
    ; Clamp end date — Bravo refuses today/future dates in the EOM dialog.
    origEndDateIso := endDateIso
    endDateIso := ClampTransfersEndDate(endDateIso)
    if (endDateIso != origEndDateIso)
        LogMessage("[" . store . "] Transfers end date clamped: " . origEndDateIso . " -> " . endDateIso . " (Bravo rejects today/future)")
    LogMessage("[" . store . "] Transfers range=" . startDateIso . ".." . endDateIso)

    outputPath := outputDir . "\" . OutputFilename(endDateIso, store, "transfers")
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
        ClickByName(T_ELEMENTS["sidebar_reports"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: double-click End of Month tile (= Preview)")
        DoubleClickByName(T_ELEMENTS["report_tile"], 8000)
        Sleep(2500)
        DismissPopups()

        ; --- Date dialog -------------------------------------------------
        ; The End of Month config dialog has a Start Date and End Date.
        ; Try ValuePattern via the SetReportDate helper first (positions 1 and
        ; 2). If the dialog doesn't support ValuePattern on these fields, we
        ; fall through with default dates — the report still runs, just for
        ; the wrong period; the orchestrator can detect that and complain.
        LogMessage("  step 3a: try SetReportDate(1, " . startDateIso . ")")
        try {
            SetReportDate(1, startDateIso)
            Sleep(600)
        } catch as e {
            LogMessage("    WARN: SetReportDate(1) failed: " . e.Message)
        }

        LogMessage("  step 3b: try SetReportDate(2, " . endDateIso . ")")
        try {
            SetReportDate(2, endDateIso)
            Sleep(600)
        } catch as e {
            LogMessage("    WARN: SetReportDate(2) failed: " . e.Message)
        }

        ; After both ValuePattern sets, push focus off the date controls so
        ; Bravo commits/validates the range and re-enables the dialog Ok
        ; button. Mirrors the LoanPortfolio2026 pattern which sleeps long
        ; after the last SetReportDate before clicking Ok.
        Send("{Tab}")
        Sleep(800)
        ActivateBravo()
        Sleep(500)

        LogMessage("  step 4: submit dialog (Enter primary, ClickByName Ok fallback)")
        ; Primary: Enter submits the modal default Ok button. This avoids
        ; the ambiguous "Ok" name lookup that can hit a wrong control when
        ; the report-tile menu is still in the UIA tree behind the dialog.
        Send("{Enter}")
        LogMessage("    [key] {Enter} sent as primary submit")
        Sleep(1500)

        ; Fallback: explicit Ok click if Enter did not submit (focus stolen).
        if !FindByName(T_ELEMENTS["preview_export"], 0) {
            LogMessage("    [fallback] Preview not yet visible, trying ClickByName(Ok)")
            try {
                ClickByName(T_ELEMENTS["config_ok"], 5000)
                LogMessage("    [UIA] clicked Ok (fallback)")
            } catch as e {
                LogMessage("    WARN: Ok click fallback failed: " . e.Message)
            }
            Sleep(1500)
        }

        ; Closing reports often take longer to render than inventory ones —
        ; give the Preview up to 60s before we declare a hang.
        if !FindByName(T_ELEMENTS["preview_export"], 60000)
            throw Error("Preview did not render within 60s (Export Document button never appeared)")
        Sleep(800)

        ; --- Step 4b: turn off Continuous Scrolling (added 2026-05-29) -----
        ; Bravo's Report Preview has an "Enable Continuous Scrolling" toggle
        ; that, when pressed, forces the entire report to render as one giant
        ; canvas. For wide year-grid reports (deposits-paid-outs), this freezes
        ; Bravo for 3+ minutes; the Export OK click then lands on a still-
        ; rendering UI and the CSV never gets written. We check the toggle
        ; state and turn it off if it's on. Wrapped so it can't itself throw.
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
        ClickByName(T_ELEMENTS["preview_export"], 5000)
        if !FindByName(T_ELEMENTS["export_ok"], 8000)
            throw Error("Export Document dialog did not appear within 8s")

        Sleep(800)
        LogMessage("  step 6: set Export format = Csv")
        SetExportFormatCsv()

        LogMessage("  step 7: set File path = " . outputPath)
        SetExportFilePath(outputPath)

        LogMessage("  step 8: uncheck open-after-export")
        UncheckOpenAfterExport()

        LogMessage("  step 9: click export OK")
        ClickByName(T_ELEMENTS["export_ok"], 5000)

        ; Longer wait — Bravo's End of Month export over the Parallels share
        ; can be slow on cold/fresh runs (up to ~2 min observed).
        if !WaitForFile(outputPath, 180)
            throw Error("CSV file did not appear at " . outputPath . " within 180s")
        Sleep(2000)  ; let Bravo finish writing before size check

        ; Reject empty/partial exports — they happen when the export starts
        ; but Bravo locks up before flushing. Require > 500 bytes (a real EoM
        ; CSV is ~11 KB).
        sz := 0
        try sz := FileGetSize(outputPath)
        if (sz < 100) {
            ; 2026-05-29: lowered from 500 to 100. Sparse reports (no transactions
            ; on the day) produce ~237-byte "No data returned" CSVs which are
            ; legitimate, not failures. 100 bytes still catches truly truncated
            ; mid-write failures (Bravo's CSV header alone is ~80 bytes).
            throw Error("Exported CSV is too small (" . sz . " bytes) — Bravo export likely failed mid-write. Path: " . outputPath)
        }
        LogMessage("  step 9b: CSV size check passed (" . sz . " bytes)")

        ; --- Robust exit sequence -----------------------------------------
        ; The Done button via UIA can leave Bravo on the Preview when state
        ; is sticky. Multi-pronged approach: Esc + Done + BackToDashboard.
        ; If any one of these returns us to Dashboard, we win.
        LogMessage("  step 10: robust exit (Esc, Done x N, BackToDashboard)")
        try ActivateBravo()
        Sleep(400)
        Send("{Escape}")
        Sleep(800)
        Loop 3 {
            if ExistsByName("Reports")
                break
            try ClickByName(T_ELEMENTS["panel_done"], 3000)
            Sleep(1200)
            DismissPopups()
        }
        ; Final fallback — call BackToDashboard with extra hops
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
