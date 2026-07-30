; ============================================================================
; reports/JewelryCountAudit.ahk
;
; Runs the "Claude Sold Inv Details" saved Custom Report from the Inventory
; sidebar for a single day (Date Sold) — all sold items with Cost, Sale
; Price, Category, Description, Date. Jewelry filtering + per-category
; piece counting happens downstream in the cloud comparison task.
;
; PURPOSE: Jewelry Count Reconciliation (2026-07-29). Nightly pull of
;   yesterday's sold items per store so the cloud task can count jewelry
;   pieces sold per category and compare against the manager's handwritten
;   EOD count posted in #end-of-day — catching fudged/missing counts before
;   inventory quietly walks out the door.
;
; ADDITIVE (Rule #4): NEW file, NEW cell (jewelry-count-audit). Does not
;   touch JewelrySoldMargin.ahk, AgedJewelrySales.ahk, SoldInvDetails.ahk,
;   or any existing cell — those belong to the separate 12-vs-18-month
;   scrap-decision project (Sold Margin Review) and must not be repurposed
;   or coupled to. Cloned from the PROVEN JewelrySoldMargin.ahk (2026-07-28,
;   confirmed working end-to-end on live Bravo 2026.6.0.79, all 5 stores)
;   rather than written from scratch, because that handler already drives
;   the exact same Inventory -> Custom Reports -> "Claude Sold Inv Details"
;   path this project needs. Only the cell name, function name, output
;   filename, and date semantics (single-day only) differ.
;
; Trigger schema (string in "date" field):
;   "YYYY-MM-DD"   — single day (this project always passes yesterday's date)
;
; Output CSV columns (verbatim from Bravo, unchanged from JewelrySoldMargin):
;   Number, Status, Category, Description, Cost, Price, Last Sold Price, Date
; ============================================================================

#Requires AutoHotkey v2.0

global JEWELRY_COUNT_AUDIT_ELEMENTS := Map(
    "sidebar_inventory",    "Inventory",
    "panel_custom_reports", "Custom Reports",
    "saved_report_value",   "Claude Sold Inv Details",
    "dialog_ok",            "Ok",
    "panel_cancel",         "Cancel",
    "layouts_caret",        "Layouts"
)

PullJewelryCountAudit(store, dateOrRange, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "jewelry-count-audit",
        "store",       store,
        "date",        dateOrRange,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    ; This project only ever passes a single day (yesterday). Range syntax
    ; is accepted for manual re-runs/backfills but the nightly trigger will
    ; always use "YYYY-MM-DD".
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
    LogMessage("[" . store . "] JewelryCountAudit startDate=" . startDate . " endDate=" . endDate)

    outputFileName := startDate . "_to_" . endDate . "_" . store . "_jewelry-count-audit.csv"
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

    ; Pre-dismiss stuck dialogs so a stranded editor never poisons this run.
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
        ClickByName(JEWELRY_COUNT_AUDIT_ELEMENTS["sidebar_inventory"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: click Custom Reports")
        ClickByName(JEWELRY_COUNT_AUDIT_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(1500)

        wantReport := JEWELRY_COUNT_AUDIT_ELEMENTS["saved_report_value"]
        LogMessage("  step 3: select saved report '" . wantReport . "'")
        if !SelectInventorySavedReport(wantReport)
            throw Error("Could not select '" . wantReport . "' from the Inventory saved-report dropdown")
        Sleep(1200)

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
            throw Error("Saved report '" . wantReport . "' did not load — refusing to run and emit misleading data")
        }
        LogMessage("    verified OK")

        LogMessage("  step 4: attempt Date Sold start override -> " . startDate)
        dateSet := 0
        try {
            SetReportDate(1, startDate)
            dateSet += 1
            Sleep(400)
        } catch as e {
            LogMessage("    NOTE: SetReportDate(1) unavailable: " . e.Message . " — continuing with saved criteria")
        }

        LogMessage("  step 5: attempt Date Sold end override -> " . endDate)
        try {
            SetReportDate(2, endDate)
            dateSet += 1
            Sleep(400)
        } catch as e {
            LogMessage("    NOTE: SetReportDate(2) unavailable: " . e.Message . " — continuing with saved criteria")
        }
        LogMessage("    date fields set: " . dateSet . "/2")

        LogMessage("  step 6: click Ok to run the report")
        Sleep(2000)
        ActivateBravo()
        Sleep(500)
        try {
            ClickByName(JEWELRY_COUNT_AUDIT_ELEMENTS["dialog_ok"], 5000)
            LogMessage("    clicked Ok by name")
        } catch as e {
            LogMessage("    WARN: Ok click failed (" . e.Message . ") — falling back to {Enter}")
            Send("{Enter}")
        }
        Sleep(2000)

        dialogGone := false
        closeCheckStart := A_TickCount
        Loop {
            stillOpen := false
            try {
                root := GetBravoRoot()
                nb := root.FindElement({AutomationId: "BoxReportName"})
                if nb
                    stillOpen := true
            }
            if (!stillOpen) {
                dialogGone := true
                break
            }
            if (A_TickCount - closeCheckStart > 20000)
                break
            if (Mod(A_Index, 3) = 0) {
                LogMessage("    dialog still open — clicking Ok again")
                try ClickByName(JEWELRY_COUNT_AUDIT_ELEMENTS["dialog_ok"], 2000)
                catch
                    Send("{Enter}")
            }
            Sleep(1500)
        }
        if (!dialogGone) {
            LogVisibleNames()
            throw Error("Report generator dialog never closed after Ok — report did not run (2026.6 regression?)")
        }
        LogMessage("    generator dialog closed — report is running")

        LogMessage("  step 6b: waiting for DataItem rows to render")
        gridReady := false
        emptyGrid := false
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
            if (A_TickCount - rendCheckStart > 180000)
                break
            Sleep(2000)
        }
        if (!gridReady) {
            try {
                root := GetBravoRoot()
                lay := root.FindElement({Name: JEWELRY_COUNT_AUDIT_ELEMENTS["layouts_caret"]})
                if lay {
                    emptyGrid := true
                    LogMessage("    [grid] rendered but returned 0 rows — treating as legitimate empty result (may mean NO_EOD_COMPARISON_DATA)")
                }
            }
            if (!emptyGrid) {
                LogVisibleNames()
                throw Error("Jewelry-count-audit grid did not render within 180s — see diag dump")
            }
        }
        Sleep(3000)
        DismissPopups()

        if (emptyGrid) {
            result["row_count"] := 0
        } else {
            LogMessage("  step 7: walk grid rows and write CSV")
            rowsWritten := WriteBuysGridToCsv(outputPath)
            if (rowsWritten < 0) {
                LogVisibleNames()
                throw Error("Failed to walk jewelry-count-audit grid (no DataItem rows found)")
            }
            LogMessage("    wrote " . rowsWritten . " data rows to CSV")
            result["row_count"] := rowsWritten
        }

        LogMessage("  step 8: exit editor -> Dashboard")
        Loop 4 {
            try ClickByName(JEWELRY_COUNT_AUDIT_ELEMENTS["panel_cancel"], 2500)
            Sleep(900)
        }
        try {
            if BackToDashboard()
                LogMessage("    confirmed back on Dashboard")
            else
                LogMessage("    WARN: BackToDashboard did not confirm — health gate will recover")
        } catch as be {
            LogMessage("    WARN: BackToDashboard threw: " . be.Message)
        }

    } catch as e {
        LogVisibleNames()
        Loop 4 {
            try ClickByName(JEWELRY_COUNT_AUDIT_ELEMENTS["panel_cancel"], 2000)
            Sleep(700)
        }
        try BackToDashboard()
        return Fail(result, started, "UIA click sequence failed: " . e.Message)
    }

    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: " . result["row_count"] . " data rows, " . result["duration_ms"] . "ms")
    return result
}
