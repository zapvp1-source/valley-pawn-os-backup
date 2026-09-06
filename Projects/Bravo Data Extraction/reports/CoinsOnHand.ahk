; ============================================================================
; reports/CoinsOnHand.ahk
;
; Runs the "Claude Coins On-Hand" saved Custom Report from the Inventory
; sidebar — snapshot of every COIN / BULLION item currently in stock for one
; store (Gold Coin, Silver Coin, Coin, Gold Bullion, Silver Bullion), with
; Cost and Price. Additive clone of ActiveInvDetails.ahk (Rule #4) plus the
; BoxReportName verification guard from AgedJewelrySales.ahk step 3b.
;
; WHY (2026-09-05): Joshua asked "do we have any gold coins for sale, what's
; the cost and price?" and nothing in the pipeline could answer it — the only
; on-hand item-level pull (active-inv-details) fails on big grids (DevExpress
; virtualiser, BRAVO_KNOWN_ISSUES 2026-08-03) and the only category-filtered
; saved reports are the jewelry ones. A category-filtered saved report keeps
; the grid small (well under the ~270-row virtualisation window) so the shared
; walker returns a complete, guard-verified result.
;
; PREREQUISITE (Bravo-side, one-time): saved report "Claude Coins On-Hand"
; must exist in the Custom Inventory Report Generator (Inventory sidebar ->
; Custom Reports). Criteria: Category IN {Gold Coin, Silver Coin, Coin, Gold
; Bullion, Silver Bullion}; Status = in stock / on shelf. Default column
; layout is fine (Number, Status, Category, Description, Cost, Price, Last
; Sold Price, Date). If the report is store-scoped it must be created in each
; of the 5 stores; if "Is Shared" works, once.
;
; UI path:
;   Dashboard -> Inventory (sidebar) -> Custom Reports
;   -> Choose Saved Report -> "Claude Coins On-Hand" -> verify BoxReportName
;   -> Ok -> grid renders -> walk grid via UIA, write CSV -> Cancel x2
;
; Trigger schema:
;   {"name": "coins-onhand", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "YYYY-MM-DD"}
;   "date" is the as-of date used in the output filename only.
;
; Output: output/<date>_<STORE>_coins-onhand.csv
; ============================================================================

#Requires AutoHotkey v2.0

global COINS_ONHAND_ELEMENTS := Map(
    "sidebar_inventory",    "Inventory",
    "panel_custom_reports", "Custom Reports",
    "saved_report_combo",   "Choose Saved Report",
    "saved_report_value",   "Claude Coins On-Hand",
    "dialog_ok",            "Ok",
    "panel_cancel",         "Cancel",
    "layouts_caret",        "Layouts"
)

PullCoinsOnHand(store, asOfDate, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "coins-onhand",
        "store",       store,
        "date",        asOfDate,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    LogMessage("[" . store . "] CoinsOnHand as-of=" . asOfDate)
    outputFileName := asOfDate . "_" . store . "_coins-onhand.csv"
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

    ; Pre-dismiss stuck dialogs (same defense as BuysFromPublic / ActiveInvDetails)
    ActivateBravo()
    Loop 4 {
        dismissed := false
        try {
            root := GetBravoRoot()
            cancelEl := root.FindElement({AutomationId: "btnCancel"})
            if cancelEl {
                try {
                    cancelEl.InvokePattern.Invoke()
                    LogMessage("    [pre-dismiss] Invoked btnCancel")
                    dismissed := true
                } catch as ie {
                    try {
                        cancelEl.Click("left")
                        dismissed := true
                    }
                }
                Sleep(900)
            }
        }
        try {
            root := GetBravoRoot()
            cancelEl := root.FindElement({AutomationId: "PART_CancelDialogButton"})
            if cancelEl {
                try {
                    cancelEl.InvokePattern.Invoke()
                    LogMessage("    [pre-dismiss] Invoked PART_CancelDialogButton")
                    dismissed := true
                    Sleep(900)
                }
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

    wantReport := COINS_ONHAND_ELEMENTS["saved_report_value"]

    try {
        DismissPopups()

        LogMessage("  step 1: open Inventory")
        ClickByName(COINS_ONHAND_ELEMENTS["sidebar_inventory"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: click Custom Reports")
        ClickByName(COINS_ONHAND_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(1500)

        LogMessage("  step 3: select saved report '" . wantReport . "'")
        ; Inventory module needs SelectInventorySavedReport (generic one does not commit).
        if !SelectInventorySavedReport(wantReport)
            throw Error("SelectInventorySavedReport: could not select " . wantReport)
        Sleep(1200)

        ; step 3b: VERIFY the selection committed (silent wrong-report guard,
        ; ported from AgedJewelrySales.ahk — the failure mode that produced the
        ; 2026-08-15 wrong jewelry counts). Re-select once, then refuse.
        LogMessage("  step 3b: verify report name committed")
        verified := false
        Loop 2 {
            loadedName := ""
            try {
                root := GetBravoRoot()
                nameBox := root.FindElement({AutomationId: "BoxReportName"})
                if nameBox {
                    try loadedName := nameBox.Value
                    if (loadedName = "")
                        try loadedName := nameBox.Name
                }
            }
            LogMessage("    BoxReportName = '" . loadedName . "'")
            if (loadedName != "" && InStr(loadedName, wantReport)) {
                verified := true
                break
            }
            if (A_Index = 1) {
                LogMessage("    WARN: report name mismatch — re-selecting once")
                try SelectInventorySavedReport(wantReport)
                Sleep(1500)
            }
        }
        if (!verified) {
            LogVisibleNames()
            throw Error("Saved report '" . wantReport . "' did not load (wrong report still active) — refusing to run and emit misleading data")
        }
        LogMessage("    verified OK")

        ; No date override — on-hand coins is "current state"
        LogMessage("  step 4: click Ok")
        Sleep(1500)
        ActivateBravo()
        Sleep(500)
        okClicked := false
        try {
            ClickByName("Ok", 5000)
            okClicked := true
            LogMessage("    clicked Ok by name")
        } catch as okErr {
            Send("{Enter}")
            LogMessage("    Ok not found (" . okErr.Message . ") -- sent {Enter} fallback")
        }
        Sleep(2000)

        ; Wait for real DataItem rows (not just the Layouts caret). Poll up to 120s.
        LogMessage("  step 4b: waiting for DataItem rows to render")
        gridReady := false
        rendCheckStart := A_TickCount
        Loop {
            try {
                root := GetBravoRoot()
                di := root.FindElements({Type: "DataItem"})
                if (di && di.Length > 0) {
                    LogMessage("    [grid] rendered with " . di.Length . " initial DataItems after " . ((A_TickCount - rendCheckStart) // 1000) . "s")
                    gridReady := true
                    break
                }
            }
            if (A_TickCount - rendCheckStart > 120000)
                break
            Sleep(2000)
        }
        if (!gridReady) {
            ; A coin-free store is a legitimate possibility. Distinguish "empty
            ; grid" from "grid never rendered": if the list view's Layouts caret
            ; is present and no DataItems exist, treat as a real zero.
            emptyGrid := false
            try {
                root := GetBravoRoot()
                lay := root.FindElement({Name: COINS_ONHAND_ELEMENTS["layouts_caret"]})
                if lay
                    emptyGrid := true
            }
            if (emptyGrid) {
                LogMessage("    [grid] list view rendered with ZERO rows — no coins/bullion on hand at " . store)
                FileAppend("Number,Status,Category,Description,Cost,Price,Last Sold Price,Date`n", outputPath, "UTF-8")
                result["row_count"] := 0
                try ClickByName(COINS_ONHAND_ELEMENTS["panel_cancel"], 3000)
                Sleep(800)
                try ClickByName(COINS_ONHAND_ELEMENTS["panel_cancel"], 3000)
                Sleep(800)
                result["output_path"] := outputPath
                result["status"]      := "success"
                result["duration_ms"] := A_TickCount - started
                LogMessage("  SUCCESS: 0 data rows (verified empty), " . result["duration_ms"] . "ms")
                return result
            }
            LogVisibleNames()
            throw Error("Grid did not render within 120s after click Ok")
        }
        Sleep(3000)
        DismissPopups()

        LogMessage("  step 5: walk grid rows and write CSV")
        rowsWritten := WriteBuysGridToCsv(outputPath)
        if (rowsWritten < 0) {
            LogVisibleNames()
            throw Error("Failed to walk coins grid (no DataItem rows found)")
        }
        LogMessage("    wrote " . rowsWritten . " data rows to CSV")
        result["row_count"] := rowsWritten

        try ClickByName(COINS_ONHAND_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        try ClickByName(COINS_ONHAND_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)

    } catch as e {
        LogVisibleNames()
        return Fail(result, started, "UIA click sequence failed: " . e.Message)
    }

    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: " . result["row_count"] . " data rows, " . result["duration_ms"] . "ms")
    return result
}
