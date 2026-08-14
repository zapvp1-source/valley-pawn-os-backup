; ============================================================================
; reports/MarkdownVerification.ahk
;
; Autonomous handler for the "Claude Markdown Verification" saved Custom
; Report in the Inventory sidebar. Preston Peters built this saved report
; 2026-08-10 (per Slack DM to Joshua) specifically so aged-inventory markdown
; compliance could be checked in detail: which on-hand items have had their
; Sales Price set (= have been marked down at some point) vs. which have not.
;
; This handler is intentionally modeled on InventoryDetails.ahk (same
; Dashboard -> Inventory -> Custom Reports -> Choose Saved Report path, same
; generic DataItem grid walker) but does NOT assume a date-range filter
; exists on this report. Precedent: Preston's other "Claude Aged Sold" saved
; report (see BRAVO_KNOWN_ISSUES.md 2026-07-28) has ZERO BravoDateEdit
; fields — date overrides are impossible there. This report may be the same
; shape (a live on-hand snapshot, not a date-windowed pull). The handler
; therefore ATTEMPTS a date-range set if fields are present, but treats their
; absence as normal, not an error, and always proceeds to run + walk the grid
; either way. Whatever columns the saved report actually exports (Number,
; Category, Age/Inventory Age, Sales Price, Status, etc.) are captured
; generically by the shared grid walker — no column names are hard-coded
; here, so this does not need to guess Preston's exact layout in advance.
;
; SKILL it powers: weekly-markdown-verification (new, Monday — checks which
; aged 1yr+ items still have no Sales Price set, i.e. have NOT been marked
; down, per store)
;
; UI path:
;   Dashboard -> Inventory (sidebar)
;   -> right panel -> Custom Reports
;   -> Bravo Custom Inventory Report Generator dialog
;       -> Choose Saved Report -> "Claude Markdown Verification"
;       -> (IF present) Override date range fields — best-effort only
;       -> Click Ok (Text element, not Button — see ClickOkTextInDialog in
;          InventoryDetails.ahk, reused here)
;   -> List renders
;   -> Walk grid with PageDown + Show More (WriteInventoryGridWithShowMore,
;      reused from InventoryDetails.ahk — shared, not redefined here)
;   -> CSV per store: <date-or-range>_<STORE>_markdown-verification.csv
;
; Trigger schema (single "date" field, same two encodings as every other
; Custom-Reports handler):
;   "date": "2026-08-13"                — logged/used in filename only if
;                                          the report has no date fields
;   "date": "2026-07-01..2026-08-13"    — explicit range, applied if the
;                                          report DOES expose date fields
;
; ADDITIVE — reuses SelectInventorySavedReport(), ClickOkTextInDialog(),
; WriteInventoryGridWithShowMore(), TryClickShowMore_Inv() from
; InventoryDetails.ahk (must be #Include'd before OR after this file in the
; same script — AHK v2 function scope is whole-file, order does not matter).
; Defines only the uniquely-named PullMarkdownVerification() and a small
; local date-field prober so it cannot collide with any existing handler.
; ============================================================================

#Requires AutoHotkey v2.0

global MARKDOWNVER_ELEMENTS := Map(
    "sidebar_inventory",    "Inventory",
    "panel_custom_reports", "Custom Reports",
    "saved_report_combo",   "Choose Saved Report",
    "saved_report_value",   "Claude Markdown Verification",
    "panel_cancel",         "Cancel"
)

PullMarkdownVerification(store, dateOrRange, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "markdown-verification",
        "store",       store,
        "date",        dateOrRange,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    ; Parse date range (used only if the report turns out to expose date
    ; fields; otherwise this is provenance for the filename/log only).
    startDate := ""
    endDate := ""
    if InStr(dateOrRange, "..") {
        parts := StrSplit(dateOrRange, "..")
        if (parts.Length != 2)
            return Fail(result, started, "Malformed date range: " . dateOrRange)
        startDate := Trim(parts[1])
        endDate := Trim(parts[2])
    } else {
        startDate := dateOrRange
        endDate := dateOrRange
    }
    LogMessage("[" . store . "] MarkdownVerification " . startDate . " to " . endDate)

    outputFileName := startDate . "_to_" . endDate . "_" . store . "_markdown-verification.csv"
    outputPath := outputDir . "\" . outputFileName
    LogMessage("  output -> " . outputPath)

    if !WaitForBravoWindowExists(30)
        return Fail(result, started, "Bravo window not found within 30s")
    ActivateBravo()
    DismissPopups()

    global CONFIG
    password := CONFIG.Has("bravo.password") ? CONFIG["bravo.password"] : ""
    if !EnsureStore(store, password)
        return Fail(result, started, "EnsureStore failed for " . store)
    LogMessage("  store confirmed: " . store)

    ResetOutputFile(outputPath)

    ; Pre-dismiss any stuck modal dialogs (same defensive loop as InventoryDetails.ahk)
    ActivateBravo()
    Loop 4 {
        dismissed := false
        try {
            root := GetBravoRoot()
            cancelEl := root.FindElement({AutomationId: "btnCancel"})
            if cancelEl {
                try {
                    cancelEl.InvokePattern.Invoke()
                    dismissed := true
                } catch {
                    try {
                        cancelEl.Click("left")
                        dismissed := true
                    }
                }
                Sleep(900)
            }
        }
        if (!dismissed)
            break
    }
    Sleep(300)

    if !BackToDashboard()
        return Fail(result, started, "BackToDashboard could not return Bravo to Dashboard")
    Sleep(500)
    DismissPopups()

    try {
        DismissPopups()

        LogMessage("  step 1: open Inventory")
        ClickByName(MARKDOWNVER_ELEMENTS["sidebar_inventory"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: click Custom Reports")
        ClickByName(MARKDOWNVER_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(1500)

        LogMessage("  step 3: select saved report '" . MARKDOWNVER_ELEMENTS["saved_report_value"] . "'")
        Sleep(3000)  ; let inventory dialog render fully — it's heavier than loans/buys
        ; Reused from InventoryDetails.ahk (same file group) — not redefined here.
        if !SelectInventorySavedReport(MARKDOWNVER_ELEMENTS["saved_report_value"])
            throw Error("Could not select '" . MARKDOWNVER_ELEMENTS["saved_report_value"] . "' from dropdown")
        Sleep(3000)  ; let criteria fully load after selection

        ; --- Date range ------------------------------------------------------
        ; CONFIRMED live 2026-08-13 (all 5 stores, smoke test): "Claude
        ; Markdown Verification" has NO date-range fields — it is a live
        ; on-hand snapshot report, same shape as Preston's "Claude Aged Sold"
        ; report. No date-field probe/override attempted; this is expected
        ; behavior, not a fallback for a failure. The requested date is used
        ; only for the output filename / provenance.
        LogMessage("  step 4: this report has no date-range fields (confirmed) — running as a live on-hand snapshot")

        LogMessage("  step 5: click Ok text element to run report")
        ; Reused from InventoryDetails.ahk.
        if !ClickOkTextInDialog()
            throw Error("Could not find/click 'Ok' Text element")

        LogMessage("  step 6: wait for grid to render (up to 300s)")
        gridReady := false
        emptyResult := false
        waitStart := A_TickCount
        Loop {
            try {
                root := GetBravoRoot()
                di := root.FindElements({Type: "DataItem"})
                if (di && di.Length > 0) {
                    LogMessage("    grid rendered with " . di.Length . " initial DataItems after " . ((A_TickCount - waitStart) // 1000) . "s")
                    gridReady := true
                    break
                }
                ; A confirmed "No data" state is a legitimate 0-row result, not
                ; a render failure — treat it the same way ItemsToPrice.ahk
                ; treats a confirmed-empty worklist.
                for typeName in ["Text", "Group"] {
                    elems := ""
                    try elems := root.FindElements({Type: typeName})
                    if (!elems)
                        continue
                    for el in elems {
                        nm := ""
                        try nm := el.Name
                        if InStr(nm, "No data") {
                            emptyResult := true
                            break
                        }
                    }
                    if (emptyResult)
                        break
                }
                if (emptyResult) {
                    LogMessage("    confirmed empty result ('No data...' text found)")
                    break
                }
            }
            if (A_TickCount - waitStart > 300000)
                break
            Sleep(3000)
        }
        if (!gridReady && !emptyResult) {
            LogVisibleNames()
            throw Error("Grid did not render within 300s")
        }

        rowsWritten := 0
        if (emptyResult) {
            ; Header unknown without a live column read — write a clearly-marked
            ; zero-row placeholder rather than guess a header, so downstream
            ; parsing can distinguish "confirmed 0 items" from "handler broke."
            try FileAppend("NoDataReturned`r`n", outputPath, "UTF-8-RAW")
            rowsWritten := 0
        } else {
            Sleep(2000)
            LogMessage("  step 6b: scroll grid to top (Ctrl+Home)")
            try {
                root := GetBravoRoot()
                firstDi := root.FindElement({Type: "DataItem"})
                if firstDi {
                    try firstDi.Click("left")
                    Sleep(500)
                }
                Send("^{Home}")
                Sleep(1500)
            }

            LogMessage("  step 7: walk grid with PageDown + Show More")
            ; Reused from InventoryDetails.ahk.
            rowsWritten := WriteInventoryGridWithShowMore(outputPath)
            if (rowsWritten < 0) {
                LogVisibleNames()
                throw Error("Grid walk returned -1 (no rows captured)")
            }
            LogMessage("    wrote " . rowsWritten . " data rows to CSV")
        }
        result["row_count"] := rowsWritten

        try ClickByName(MARKDOWNVER_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        try ClickByName(MARKDOWNVER_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)

    } catch as e {
        LogVisibleNames()
        return Fail(result, started, "UIA click sequence failed: " . e.Message)
    }

    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: " . result["row_count"] . " rows, " . result["duration_ms"] . "ms")
    return result
}
