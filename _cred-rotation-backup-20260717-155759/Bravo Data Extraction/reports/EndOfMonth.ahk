; ============================================================================
; reports/EndOfMonth.ahk
;
; Pulls Bravo's "End of Month" report for a single store and exports it as CSV.
; This is a BUILT-IN Bravo report (not a saved Ad Hoc), accessed via:
;   Dashboard -> Reports (sidebar)
;   -> Closing Reports section -> End of Month (tile)
;   -> Date Range config dialog -> set Start/End -> Ok
;   -> Report Preview renders
;   -> Export Document -> Csv (or other format) -> save path -> OK
;   -> Done x2 back to Dashboard
;
; SKILL it powers: monday-store-rankings — the 8-metric leaderboard derives
; from per-store End of Month reports (Ending Loan Base, Ending Inventory
; Base, Sales Revenue, Pawn Service Charges from daily Interest+Fees totals,
; Layaway activity, etc.).
;
; Cloned from AgedInventorySummary.ahk (same Preview → Export pattern).
; Differences:
;   - report tile name "End of Month" instead of "Aged Inventory Summary"
;   - report has a date RANGE (Start + End) not just a single Date
;   - parent section is "Closing Reports" not "Inventory Reports"
;
; Trigger schema:
;   "stores": ["CUL","HAR","LEX","ROA","WAY"]   — per-store invocation
;   "date":   "YYYY-MM-DD..YYYY-MM-DD"          — start..end of reporting period
;
; Output filename: <END_DATE>_<STORE>_end-of-month.csv
; ============================================================================

#Requires AutoHotkey v2.0

; ----------------------------------------------------------------------------
; ClampEomEndDate(yyyymmdd)
; Bravo's End of Month report calendar refuses today and future dates — Ok
; stays disabled if the bound DatePicker value is >= today. ValuePattern can
; paint the inner Edit's text, but the underlying control rejects the commit
; on Ok-click. Workaround: if the requested end date is today or later, clamp
; it to yesterday. Logged so the caller knows.
; ----------------------------------------------------------------------------
ClampEomEndDate(yyyymmdd) {
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


; ---------------------------------------------------------------------------
; Hang-prevention helpers (added 2026-06-08)
; Root cause of the recurring "(Not Responding)": the export dialog's CSV
; format selection was UNVERIFIABLE (the DevExpress combo reads Value='' even
; on success), so a run could click export OK with the format NOT actually set
; to CSV. Bravo then tried to export the wide End-of-Month report in the wrong
; format, pinned its UI thread (Windows marks it "Not Responding"), and never
; wrote the .csv -- wedging the preview and cascading every later store.
; Fix: verify CSV the way Joshua does by eye (the File-path field auto-renames
; to a .csv extension), abort cleanly if it can't be confirmed (never click OK
; blind), and gate clicks on an IsHungAppWindow check so we never drive UIA
; into a frozen window.
; ---------------------------------------------------------------------------
EomBravoHwnd() {
    global BRAVO_WIN_TITLE
    return WinExist(BRAVO_WIN_TITLE)
}

; Wait up to timeoutMs for Bravo to be responsive. Returns false if still hung.
EomWaitResponsive(timeoutMs := 20000) {
    deadline := A_TickCount + timeoutMs
    loop {
        hwnd := EomBravoHwnd()
        if hwnd && !DllCall("IsHungAppWindow", "Ptr", hwnd)
            return true
        if (A_TickCount > deadline)
            return false
        Sleep(500)
    }
}

; Read the export dialog's File path edit value ("" if unreadable). Used to
; confirm the CSV format took (Bravo auto-flips the path extension to .csv).
EomExportPathValue() {
    try {
        layout := FindByName(SRJ_ELEMENTS["export_file_path"], 1500)
        if !layout
            return ""
        edit := layout.FindElement({Type: "Edit"})
        if !edit
            return ""
        return edit.Value
    }
    return ""
}

; Select CSV in the Export format combo the human way (focus, type Csv, Tab)
; and VERIFY via the file-path extension flipping to .csv. Retries up to 3x.
; Returns true only when confirmed.
EomSelectCsvVerified() {
    combo := FindExportField("Export format", "ComboBox")
    if !combo {
        LogMessage("    [csv] Export format combo not found")
        return false
    }
    Loop 3 {
        LogMessage("    [csv] attempt " . A_Index . ": focus combo, type Csv, Tab")
        try {
            try combo.Focus()
            Sleep(300)
            Send("!{Down}")
            Sleep(600)
            Send("Xlsx")
            Sleep(400)
            Send("{Tab}")
            Sleep(1200)
        } catch as e {
            LogMessage("    [csv] keyboard select error: " . e.Message)
        }
        pathVal := EomExportPathValue()
        if (pathVal != "" && RegExMatch(pathVal, "i)\.xlsx\s*$")) {
            LogMessage("    [csv] confirmed via path extension: '" . pathVal . "'")
            return true
        }
        if SecComboHasValue(combo, "Xlsx") {
            LogMessage("    [csv] confirmed via combo Value")
            return true
        }
        LogMessage("    [csv] not confirmed (path='" . pathVal . "'); retrying")
        Sleep(600)
    }
    return false
}

global EOM_ELEMENTS := Map(
    "sidebar_reports",    "Reports",
    "report_tile",        "End of Month",
    "config_ok",          "Ok",
    "preview_export",     "Export...",
    "export_ok",          "OK",
    "panel_done",         "Done"
)

PullEndOfMonth(store, dateOrRange, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "end-of-month",
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
    endDateIso := ClampEomEndDate(endDateIso)
    if (endDateIso != origEndDateIso)
        LogMessage("[" . store . "] EndOfMonth end date clamped: " . origEndDateIso . " -> " . endDateIso . " (Bravo rejects today/future)")
    LogMessage("[" . store . "] EndOfMonth range=" . startDateIso . ".." . endDateIso)

    outputPath := StrReplace(outputDir . "\" . OutputFilename(endDateIso, store, "end-of-month"), ".csv", ".xlsx")
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

    ; --- Local-export path (2026-06-08) -------------------------------
    ; EOM is a wide ~11 KB report; writing it synchronously to the
    ; Parallels SMB share pins Bravo's UI thread mid-write and wedges it
    ; (the <=1 KB working reports never trip it). So export to the local
    ; temp disk first, then copy the finished CSV to the Y: output dir.
    localExportDir := A_Temp . "\BravoExport"
    try DirCreate(localExportDir)
    localExportPath := StrReplace(localExportDir . "\" . OutputFilename(endDateIso, store, "end-of-month"), ".csv", ".xlsx")
    ResetOutputFile(outputPath)
    ResetOutputFile(localExportPath)

    if !BackToDashboard()
        return Fail(result, started, "BackToDashboard could not return Bravo to Dashboard")
    Sleep(500)
    DismissPopups()

    try {
        DismissPopups()

        LogMessage("  step 1: open Reports")
        ClickByName(EOM_ELEMENTS["sidebar_reports"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: double-click End of Month tile (= Preview)")
        DoubleClickByName(EOM_ELEMENTS["report_tile"], 8000)
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
        if !FindByName(EOM_ELEMENTS["preview_export"], 0) {
            LogMessage("    [fallback] Preview not yet visible, trying ClickByName(Ok)")
            try {
                ClickByName(EOM_ELEMENTS["config_ok"], 5000)
                LogMessage("    [UIA] clicked Ok (fallback)")
            } catch as e {
                LogMessage("    WARN: Ok click fallback failed: " . e.Message)
            }
            Sleep(1500)
        }

        ; Closing reports often take longer to render than inventory ones —
        ; give the Preview up to 60s before we declare a hang.
        if !FindByName(EOM_ELEMENTS["preview_export"], 60000)
            throw Error("Preview did not render within 60s (Export Document button never appeared)")
        Sleep(800)

        ; [CS toggle block removed 2026-06-07 — it was inducing the Not-Responding hang; export straight from the default paginated preview, same as manual]
        ; --- Hardened export (2026-06-08): verify CSV before OK and gate every
        ; click on a responsiveness check so we never drive UIA into a
        ; rendering/hung window (the documented cascade trigger). ----------
        if !EomWaitResponsive(30000)
            throw Error("Bravo not responsive after preview render; aborting before export to avoid a wedge")

        LogMessage("  step 5: open Export Document dialog")
        ClickByName(EOM_ELEMENTS["preview_export"], 5000)
        if !FindByName(EOM_ELEMENTS["export_ok"], 8000)
            throw Error("Export Document dialog did not appear within 8s")
        Sleep(800)
        LogMessage("  step 6: set Export format = Xlsx via format dropdown click")
        combo := FindExportField("Export format", "ComboBox")
        if !combo
            throw Error("Export format combo not found")
        xlsxSet := false
        candNames := ["Xlsx", "Xlsx File", "XLSX File"]
        pathVal := ""
        Loop 3 {
            LogMessage("    [xlsx] round " . A_Index . ": open format dropdown")
            try {
                combo.Click("left")
                Sleep(700)
            } catch as e {
                LogMessage("    [xlsx] combo open err: " . e.Message)
            }
            for nm in candNames {
                try {
                    ClickByName(nm, 1500)
                    Sleep(900)
                } catch as e {
                    continue
                }
                pathVal := EomExportPathValue()
                if InStr(pathVal, ".xlsx") {
                    LogMessage("    [xlsx] confirmed via item " . nm . " path=" . pathVal)
                    xlsxSet := true
                    break
                }
            }
            if xlsxSet
                break
            LogMessage("    [xlsx] round not confirmed; retrying")
            Sleep(500)
        }
        if !xlsxSet
            throw Error("Could not set Export format to Xlsx after dropdown attempts")

        LogMessage("  step 7: set File path (local) = " . localExportPath)
        SetExportFilePath(localExportPath)

        LogMessage("  step 8: uncheck open-after-export")
        UncheckOpenAfterExport()

        ; Responsiveness gate immediately before the commit.
        if !EomWaitResponsive(15000)
            throw Error("Bravo went unresponsive before export OK; aborting")

        LogMessage("  step 9: click export OK")
        ClickByName(EOM_ELEMENTS["export_ok"], 5000)

        ; After OK, Bravo writes the CSV to the LOCAL temp disk (fast).
        ; Poll only the filesystem; log responsiveness for diagnostics but
        ; fire no UIA at the window.
        gotFile := false
        waitDeadline := A_TickCount + 240000
        Loop {
            if FileExist(localExportPath) {
                lsz := 0
                try lsz := FileGetSize(localExportPath)
                if (lsz > 0) {
                    gotFile := true
                    break
                }
            }
            if (A_TickCount > waitDeadline)
                break
            hwnd := EomBravoHwnd()
            hung := (hwnd && DllCall("IsHungAppWindow", "Ptr", hwnd)) ? "yes" : "no"
            LogMessage("    [export-wait] local-file=" . (FileExist(localExportPath) ? "exists" : "no") . " bravo-hung=" . hung)
            Sleep(4000)
        }
        if !gotFile
            throw Error("CSV did not appear at local path " . localExportPath . " within 240s")

        Sleep(1500)  ; let Bravo finish flushing the local write
        ; Copy the finished local CSV to the Y: output folder the pipeline expects.
        try FileCopy(localExportPath, outputPath, true)
        if !WaitForFile(outputPath, 30)
            throw Error("Local CSV written but copy to share failed: " . outputPath)

        ; Reject empty/partial exports. A real EoM CSV is ~11 KB.
        sz := 0
        try sz := FileGetSize(outputPath)
        if (sz < 500) {
            throw Error("Exported CSV is too small (" . sz . " bytes) — export likely failed mid-write. Path: " . outputPath)
        }
        LogMessage("  step 9b: CSV size check passed (" . sz . " bytes); local->share copy ok")

        ; --- Exit sequence (2026-06-19): match SafeRegisterJournal's PROVEN exit.
        ; Two UNCONDITIONAL Done clicks (exit preview, then exit reports list),
        ; exactly like SRJ which never sticks. Dropped Send("{Escape}") (it left
        ; the preview in a state where Done went dead) and dropped the early
        ; ExistsByName("Reports") break (the Reports MENU false-matches "Reports"
        ; and stranded Bravo there). BackToDashboard is only a final safety net.
        LogMessage("  step 10: exit preview (Done x2, SRJ pattern)")
        try ActivateBravo()
        Sleep(400)
        try ClickByName(EOM_ELEMENTS["panel_done"], 3000)   ; exit preview
        Sleep(1200)
        DismissPopups()
        try ClickByName(EOM_ELEMENTS["panel_done"], 3000)   ; exit reports list
        Sleep(1200)
        DismissPopups()
        if !ExistsByName("Reports") {
            LogMessage("  step 10b: BackToDashboard safety net")
            BackToDashboard(8)
        }
        Sleep(500)
        DismissPopups()

    } catch as e {
        ; NOTE 2026-06-08: removed LogVisibleNames() here -- a full UIA tree
        ; enumeration hangs against a wedged/rendering Bravo and deepens the
        ; cascade. The recovery block below already screenshots state.
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

    rowCount := 1
    result["row_count"]   := rowCount
    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: " . rowCount . " rows, " . result["duration_ms"] . "ms")
    return result
}
