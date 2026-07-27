; ============================================================================
; reports/SoldInvDetails.ahk
;
; Runs the "Claude Sold Inv Details" saved Custom Report from the Inventory
; sidebar — all items SOLD within a configurable date range, for one store.
;
; SKILL it powers: deep-kpi-buys (Phase 8 — buys × inventory × sales join)
;
; UI path:
;   Dashboard -> Inventory (sidebar)
;   -> right panel -> Custom Reports
;   -> Bravo Custom Inventory Report Generator dialog
;       -> Choose Saved Report -> "Claude Sold Inv Details"
;       -> Override Date Sold start/end (positions 1 and 2)
;       -> Ok
;   -> List renders with all items sold in the period
;   -> Walk grid via UIA, write CSV
;   -> Cancel x2 back to Dashboard
;
; Trigger schema (string in "date" field):
;   "YYYY-MM-DD"                       — single day
;   "YYYY-MM-DD..YYYY-MM-DD"           — explicit range
;
; Output CSV columns: whatever the saved report exports. Expected includes
; Inventory #, Category, Description, Cost, Sale Price, Date Sold,
; Days On Shelf, Acquired Date, Acquired Ticket #, Store.
; ============================================================================

#Requires AutoHotkey v2.0

global SOLD_INV_ELEMENTS := Map(
    "sidebar_inventory",    "Inventory",
    "panel_custom_reports", "Custom Reports",
    "saved_report_combo",   "Choose Saved Report",
    "saved_report_value",   "Claude Sold Inv Details",
    "dialog_ok",            "Ok",
    "panel_cancel",         "Cancel",
    "layouts_caret",        "Layouts"
)

PullSoldInvDetails(store, dateOrRange, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "sold-inv-details",
        "store",       store,
        "date",        dateOrRange,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

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
    LogMessage("[" . store . "] SoldInvDetails startDate=" . startDate . " endDate=" . endDate)

    outputFileName := startDate . "_to_" . endDate . "_" . store . "_sold-inv-details.csv"
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

    ; Pre-dismiss stuck dialogs
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
        ClickByName(SOLD_INV_ELEMENTS["sidebar_inventory"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: click Custom Reports")
        ClickByName(SOLD_INV_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(1500)

        LogMessage("  step 3: select saved report '" . SOLD_INV_ELEMENTS["saved_report_value"] . "'")
        SelectSavedReport(SOLD_INV_ELEMENTS["saved_report_combo"], SOLD_INV_ELEMENTS["saved_report_value"])
        Sleep(1000)

        ; Override Date Sold range (positions 1 and 2)
        LogMessage("  step 4: override Start Date to " . startDate)
        try {
            SetReportDate(1, startDate)
        } catch as e {
            LogMessage("    WARN: SetReportDate(1) failed: " . e.Message)
            LogVisibleNames()
            throw Error("Could not set Start Date — see LogVisibleNames dump")
        }
        Sleep(400)

        LogMessage("  step 5: override End Date to " . endDate)
        try {
            SetReportDate(2, endDate)
        } catch as e {
            LogMessage("    WARN: SetReportDate(2) failed: " . e.Message)
            LogVisibleNames()
            throw Error("Could not set End Date — see LogVisibleNames dump")
        }
        Sleep(400)

        LogMessage("  step 6: send Enter to dialog (default button = Ok/Run)")
        Sleep(2500)
        ActivateBravo()
        Sleep(500)
        Send("{Enter}")
        LogMessage("    sent {Enter}")
        Sleep(2000)

        ; Wait for DataItem rows (real grid signal), not Layouts caret which can
        ; appear in the dialog too.
        LogMessage("  step 6b: waiting for DataItem rows to render")
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
            LogVisibleNames()
            throw Error("Sold inv grid did not render within 120s — see diag dump")
        }
        Sleep(3000)
        DismissPopups()

        LogMessage("  step 7: walk grid rows and write CSV")
        ; Reuse WriteBuysGridToCsv — generic DevExpress DataItem walker.
        rowsWritten := WriteBuysGridToCsv(outputPath)
        if (rowsWritten < 0) {
            LogVisibleNames()
            throw Error("Failed to walk sold inv grid (no DataItem rows found)")
        }
        LogMessage("    wrote " . rowsWritten . " data rows to CSV")
        result["row_count"] := rowsWritten

        try ClickByName(SOLD_INV_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        try ClickByName(SOLD_INV_ELEMENTS["panel_cancel"], 3000)
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
