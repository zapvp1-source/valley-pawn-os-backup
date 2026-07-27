; ============================================================================
; reports/ActiveInvDetails.ahk
;
; Runs the "Claude Active Inv Details" saved Custom Report from the Inventory
; sidebar — snapshot of all items currently ON THE SHELF for one store.
;
; SKILL it powers: deep-kpi-buys (Phase 8 — buys × inventory join)
;
; UI path:
;   Dashboard -> Inventory (sidebar)
;   -> right panel -> Custom Reports
;   -> Bravo Custom Inventory Report Generator dialog
;       -> Choose Saved Report -> "Claude Active Inv Details"
;       -> Ok (no date override — this is a current-state report)
;   -> List renders with all on-shelf items
;   -> Walk grid via UIA, write CSV
;   -> Cancel x2 back to Dashboard
;
; Trigger schema:
;   "date": "YYYY-MM-DD"   — captured as the "as-of" date in the output filename
;
; Output CSV columns: whatever the saved report exports. Expected includes
; Inventory #, Category, Description, Cost, Asking Price, Days On Shelf,
; Acquired Date, Acquired Ticket #, Store.
; ============================================================================

#Requires AutoHotkey v2.0

global ACTIVE_INV_ELEMENTS := Map(
    "sidebar_inventory",    "Inventory",
    "panel_custom_reports", "Custom Reports",
    "saved_report_combo",   "Choose Saved Report",
    "saved_report_value",   "Claude Active Inv Details",
    "dialog_ok",            "Ok",
    "panel_cancel",         "Cancel",
    "layouts_caret",        "Layouts"
)

PullActiveInvDetails(store, asOfDate, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "active-inv-details",
        "store",       store,
        "date",        asOfDate,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    LogMessage("[" . store . "] ActiveInvDetails as-of=" . asOfDate)
    outputFileName := asOfDate . "_" . store . "_active-inv-details.csv"
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

    ; Pre-dismiss stuck dialogs (same defense as BuysFromPublic)
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

    try {
        DismissPopups()

        LogMessage("  step 1: open Inventory")
        ClickByName(ACTIVE_INV_ELEMENTS["sidebar_inventory"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: click Custom Reports")
        ClickByName(ACTIVE_INV_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(1500)

        LogMessage("  step 3: select saved report '" . ACTIVE_INV_ELEMENTS["saved_report_value"] . "'")
        SelectSavedReport(ACTIVE_INV_ELEMENTS["saved_report_combo"], ACTIVE_INV_ELEMENTS["saved_report_value"])
        Sleep(1000)

        ; No date override — active inventory is "current state"
        LogMessage("  step 4: send Enter to dialog (default button = Ok/Run)")
        Sleep(2500)
        ActivateBravo()
        Sleep(500)
        Send("{Enter}")
        LogMessage("    sent {Enter}")
        Sleep(2000)

        ; Wait for the actual data rows (DataItem control type) to appear, not
        ; just the Layouts text element (which exists in both dialog AND list
        ; view in the Inventory module — false positive). Poll up to 120s.
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
            ; Dump button list so we can see what's actually rendered when the
            ; grid doesn't show up. Helps identify if a Run/Preview/Show button
            ; needs to be clicked separately, or if a confirmation dialog is up.
            try {
                root := GetBravoRoot()
                btns := root.FindElements({Type: "Button"})
                LogMessage("    [no-grid-diag] visible+enabled+named buttons:")
                shown := 0
                for b in btns {
                    try {
                        n := b.Name
                        off := b.IsOffscreen
                        en := b.IsEnabled
                        if (n != "" && !off && en) {
                            shown++
                            if (shown <= 40)
                                LogMessage("      Button '" . SubStr(n, 1, 60) . "' autoId='" . b.AutomationId . "'")
                        }
                    }
                }
                LogMessage("    [no-grid-diag] total named buttons: " . shown)
            }
            LogVisibleNames()
            throw Error("Grid did not render within 120s after click Ok — see diag dump")
        }
        Sleep(3000)  ; let scrolling catch up
        DismissPopups()

        LogMessage("  step 5: walk grid rows and write CSV")
        rowsWritten := WriteBuysGridToCsv(outputPath)
        if (rowsWritten < 0) {
            LogVisibleNames()
            throw Error("Failed to walk active inv grid (no DataItem rows found)")
        }
        LogMessage("    wrote " . rowsWritten . " data rows to CSV")
        result["row_count"] := rowsWritten

        try ClickByName(ACTIVE_INV_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        try ClickByName(ACTIVE_INV_ELEMENTS["panel_cancel"], 3000)
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
