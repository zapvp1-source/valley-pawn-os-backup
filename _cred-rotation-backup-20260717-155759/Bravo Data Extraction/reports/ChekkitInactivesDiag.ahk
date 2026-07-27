; ============================================================================
; reports/ChekkitInactivesDiag.ahk
;
; One-shot diagnostic. Opens Customers -> Custom Reports, selects the SHARED
; 'Chekkit Inactives' saved report from the dropdown, then DUMPS all visible
; UIA elements in the open Custom Customer Report Generator dialog BEFORE
; clicking Ok. This reveals (a) what criteria controls exist for building V2,
; and (b) what values the broken saved report has loaded.
;
; Cell name: chekkit-inactives-diag
; Trigger payload: {"name":"chekkit-inactives-diag","stores":["CUL"],"date":"YYYY-MM-DD"}
;
; DOES NOT click Ok and DOES NOT walk the grid. Cancels out cleanly.
; ============================================================================
#Requires AutoHotkey v2.0

global CHEKKIT_DIAG_ELEMENTS := Map(
    "sidebar_customers",    "Customers",
    "panel_custom_reports", "Custom Reports",
    "saved_report_combo",   "Choose Saved Report",
    "saved_report_value",   "Chekkit Inactives",
    "panel_cancel",         "Cancel"
)

PullChekkitInactivesDiag(store, date, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "chekkit-inactives-diag",
        "store",       store,
        "date",        date,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    LogMessage("[" . store . "] ChekkitInactivesDiag date=" . date)

    if !WaitForBravoReady(30)
        return Fail(result, started, "Bravo window not found/ready within 30s")

    ActivateBravo()
    DismissPopups()

    global CONFIG
    password := CONFIG.Has("bravo.password") ? CONFIG["bravo.password"] : ""
    if !EnsureStore(store, password)
        return Fail(result, started, "EnsureStore failed for " . store)
    LogMessage("  store confirmed: " . store)

    if !BackToDashboard()
        return Fail(result, started, "BackToDashboard could not return Bravo to Dashboard")
    Sleep(500)
    DismissPopups()

    try {
        DismissPopups()
        LogMessage("  step 1: open Customers")
        ClickByName(CHEKKIT_DIAG_ELEMENTS["sidebar_customers"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: click Custom Reports in right panel")
        ClickByName(CHEKKIT_DIAG_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(1500)

        ; ====== DUMP A — empty criteria builder, before loading saved report ======
        LogMessage("  ====== DUMP A: empty Custom Customer Report Generator dialog ======")
        LogVisibleNames(120)

        LogMessage("  step 3: select 'Chekkit Inactives' from Choose Saved Report dropdown")
        SelectSavedReport(CHEKKIT_DIAG_ELEMENTS["saved_report_combo"], CHEKKIT_DIAG_ELEMENTS["saved_report_value"])
        Sleep(1500)

        ; ====== DUMP B — criteria builder with 'Chekkit Inactives' loaded ======
        LogMessage("  ====== DUMP B: criteria builder with Chekkit Inactives loaded ======")
        LogVisibleNames(120)

        ; Cancel out — do NOT click Ok, do NOT run the report
        LogMessage("  cancel out (no Ok click)")
        try ClickByName(CHEKKIT_DIAG_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        try ClickByName(CHEKKIT_DIAG_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)

        try BackToDashboard()
    } catch as e {
        return Fail(result, started, "Diag click sequence failed: " . e.Message)
    }

    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: diag complete, " . result["duration_ms"] . "ms")
    return result
}

