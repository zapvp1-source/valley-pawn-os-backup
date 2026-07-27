; ============================================================================
; reports/ChekkitInvitesRange.ahk
; Catch-up Chekkit invite pull over an explicit "First Time In" date range.
; ADDITIVE — nothing existing modified. Cell name: chekkit-invites-range.
;
; Reuses the PROVEN intake pipeline pieces (2026-06-30 fix):
;   - EnsureStore()                     store switch w/ saved password (lib)
;   - IntakeSelectSavedReportCommitted() bottom-most-combo + wheel + REAL click
;   - IntakeGetLoadedReportName()       read BoxReportName to verify selection
;   - IntakeClickOkVerified()           reliable Ok-run
;   - SetReportDate(pos,"YYYY-MM-DD")   set First Time In start/end by position
;   - ScrollAndCollectChekkitRows()     virtualized-grid scroll+accumulate
;     (from ChekkitGridOnly.ahk) -> rows of Map("phone","email","dnt")
;
; Saved report lives under Customers -> Custom Reports, name "Chekkit Invites 2"
; (exact case). Trigger "date" field carries "YYYY-MM-DD..YYYY-MM-DD".
; Exits via the named "Cancel" button (never "Done") per KNOWN_ISSUES.
; ============================================================================
#Requires AutoHotkey v2.0

global CHEKKIT_RANGE_ELEMENTS := Map(
    "sidebar_customers",    "Customers",
    "panel_custom_reports", "Custom Reports",
    "saved_report_combo",   "Choose Saved Report",
    "saved_report_value",   "Chekkit Invites 2",
    "layouts_caret",        "Layouts",
    "panel_cancel",         "Cancel"
)

PullChekkitInvitesRange(store, dateOrRange, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "chekkit-invites-range",
        "store",       store,
        "date",        dateOrRange,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    ; --- Parse "YYYY-MM-DD..YYYY-MM-DD" (or single day) -----------------------
    startDate := ""
    endDate := ""
    if InStr(dateOrRange, "..") {
        parts := StrSplit(dateOrRange, "..")
        if (parts.Length != 2)
            return Fail(result, started, "Malformed date range: " . dateOrRange)
        startDate := Trim(parts[1])
        endDate := Trim(parts[2])
    } else {
        startDate := Trim(dateOrRange)
        endDate := Trim(dateOrRange)
    }

    outputPath := outputDir . "\" . OutputFilename(endDate, store, "chekkit-invites-range")
    LogMessage("[" . store . "] ChekkitInvitesRange range=" . startDate . ".." . endDate . " -> " . outputPath)

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
        LogMessage("  step 1: open Customers")
        ClickByName(CHEKKIT_RANGE_ELEMENTS["sidebar_customers"], 8000)
        Sleep(1500)
        DismissPopups()
        LogMessage("  step 2: click Custom Reports")
        ClickByName(CHEKKIT_RANGE_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(2000)

        ; --- Select saved report, verify by BoxReportName, retry up to 3 -----
        selected := false
        Loop 3 {
            selAttempt := A_Index
            LogMessage("  step 3: select saved report 'Chekkit Invites 2' (attempt " . selAttempt . ")")
            IntakeSelectSavedReportCommitted(CHEKKIT_RANGE_ELEMENTS["saved_report_combo"], CHEKKIT_RANGE_ELEMENTS["saved_report_value"])
            Sleep(1200)
            loadedName := IntakeGetLoadedReportName()
            LogMessage("    [saved-report] BoxReportName='" . loadedName . "'")
            if (InStr(loadedName, "Chekkit Invites 2")) {
                selected := true
                break
            }
            LogMessage("    [saved-report] not committed; retrying selection")
            Sleep(800)
        }
        if (!selected)
            throw Error("Could not commit 'Chekkit Invites 2' selection after 3 attempts")

        ; --- Set First Time In range (pos 1 = start, pos 2 = end) ------------
        LogMessage("  step 4: set First Time In " . startDate . " .. " . endDate)
        try {
            SetReportDate(1, startDate)
        } catch as e {
            LogMessage("    WARN SetReportDate(1): " . e.Message)
        }
        try {
            SetReportDate(2, endDate)
        } catch as e {
            LogMessage("    WARN SetReportDate(2): " . e.Message)
        }
        Sleep(800)

        ; --- Run report -----------------------------------------------------
        LogMessage("  step 5: click Ok to run (verified)")
        IntakeClickOkVerified()
        if !FindByName(CHEKKIT_RANGE_ELEMENTS["layouts_caret"], 30000)
            throw Error("Customer list did not render within 30s (no Layouts caret)")
        Sleep(5000)

        ; --- Walk the grid (scroll + accumulate) ----------------------------
        LogMessage("  step 6: scroll+accumulate grid and write CSV")
        rows := ScrollAndCollectChekkitRows()
        FileAppend("first_name,last_name,phone,email,dnt,last_visit`r`n", outputPath, "UTF-8-RAW")
        count := 0
        for r in rows {
            dntStr := r["dnt"] ? "DNT" : ""
            WriteCsvRow(outputPath, r.Has("name") ? r["name"] : "", "", r["phone"], r["email"], dntStr, "")
            count++
        }
        LogMessage("    wrote " . count . " rows to CSV")
        result["row_count"] := count

        ; --- Exit via Cancel x2 (never Done) --------------------------------
        try ClickByName(CHEKKIT_RANGE_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        try ClickByName(CHEKKIT_RANGE_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
    } catch as e {
        try ClickByName(CHEKKIT_RANGE_ELEMENTS["panel_cancel"], 2000)
        Sleep(500)
        try ClickByName(CHEKKIT_RANGE_ELEMENTS["panel_cancel"], 2000)
        return Fail(result, started, "ChekkitInvitesRange failed: " . e.Message)
    }

    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: " . result["row_count"] . " rows, " . result["duration_ms"] . "ms")
    return result
}
