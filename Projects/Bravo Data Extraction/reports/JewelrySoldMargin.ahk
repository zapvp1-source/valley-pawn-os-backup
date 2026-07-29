; ============================================================================
; reports/JewelrySoldMargin.ahk
;
; Runs the "Claude Sold Inv Details" saved Custom Report from the Inventory
; sidebar for a Date Sold range — all sold items with Cost, Sale Price,
; Date Sold, Days On Shelf, Acquired Date, Category. Jewelry filtering
; happens in post-processing (Category column).
;
; PURPOSE: the 12-vs-18-month jewelry scrap decision (2026-07-28).
;   Per-piece margin by age-at-sale + buy-to-sell lag. Joshua's
;   "Aged Jewelry Sales" saved report returns 0 rows as-saved (verified
;   clean on 2026.6.0.79 with the Inventory-module selector) — its criteria
;   need fixing inside Bravo. This handler uses the proven
;   "Claude Sold Inv Details" report instead, which carries the exact
;   columns the margin analysis needs.
;
; ADDITIVE (Rule #4): NEW file, NEW cell (jewelry-margin-sold). Does not
;   touch SoldInvDetails.ahk (which uses the generic selector that fails in
;   the Inventory module) or any existing cell. Cloned from
;   AgedJewelrySales.ahk (2026-07-28), which is itself proven end-to-end on
;   Bravo 2026.6.0.79 (selection, verify, run, exit).
;
; Trigger schema (string in "date" field):
;   "YYYY-MM-DD..YYYY-MM-DD"  — Date Sold range (positions 1 and 2)
;   "YYYY-MM-DD"              — single day
;   "saved"                   — run exactly as saved, no date override
; ============================================================================

#Requires AutoHotkey v2.0

global JEWELRY_SOLD_MARGIN_ELEMENTS := Map(
    "sidebar_inventory",    "Inventory",
    "panel_custom_reports", "Custom Reports",
    "saved_report_value",   "Claude Sold Inv Details",
    "dialog_ok",            "Ok",
    "panel_cancel",         "Cancel",
    "layouts_caret",        "Layouts"
)

PullJewelrySoldMargin(store, dateOrRange, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "jewelry-margin-sold",
        "store",       store,
        "date",        dateOrRange,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    useSavedCriteria := (StrLower(Trim(dateOrRange)) = "saved")

    startDate := ""
    endDate := ""
    if (useSavedCriteria) {
        startDate := "saved"
        endDate := "saved"
    } else if InStr(dateOrRange, "..") {
        parts := StrSplit(dateOrRange, "..")
        if (parts.Length != 2)
            return Fail(result, started, "Malformed date range: " . dateOrRange)
        startDate := Trim(parts[1])
        endDate := Trim(parts[2])
    } else {
        startDate := dateOrRange
        endDate := dateOrRange
    }
    LogMessage("[" . store . "] JewelrySoldMargin startDate=" . startDate . " endDate=" . endDate)

    outputFileName := (useSavedCriteria ? "saved_" . store : startDate . "_to_" . endDate . "_" . store) . "_jewelry-margin-sold.csv"
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
        ClickByName(JEWELRY_SOLD_MARGIN_ELEMENTS["sidebar_inventory"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: click Custom Reports")
        ClickByName(JEWELRY_SOLD_MARGIN_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(1500)

        wantReport := JEWELRY_SOLD_MARGIN_ELEMENTS["saved_report_value"]
        LogMessage("  step 3: select saved report '" . wantReport . "'")
        ; Inventory module REQUIRES SelectInventorySavedReport — the generic
        ; SelectSavedReport fills BoxReportName without committing criteria.
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

        dateSet := 0
        if (useSavedCriteria) {
            LogMessage("  step 4/5: SKIPPED date override — running report as saved in Bravo")
        } else {
            LogMessage("  step 4: attempt Date Sold start override -> " . startDate)
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
        }

        ; On Bravo 2026.6.0.79 the Enter-as-default-button shortcut is not
        ; reliably firing the generator's Ok. Click Ok explicitly by name;
        ; Enter stays as fallback only.
        LogMessage("  step 6: click Ok to run the report")
        Sleep(2000)
        ActivateBravo()
        Sleep(500)
        okClicked := false
        try {
            ClickByName(JEWELRY_SOLD_MARGIN_ELEMENTS["dialog_ok"], 5000)
            okClicked := true
            LogMessage("    clicked Ok by name")
        } catch as e {
            LogMessage("    WARN: Ok click failed (" . e.Message . ") — falling back to {Enter}")
            Send("{Enter}")
        }
        Sleep(2000)

        ; Confirm the generator dialog actually closed. If BoxReportName is
        ; still reachable, the report never ran — a 0-row result from here
        ; would be a lie.
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
                try ClickByName(JEWELRY_SOLD_MARGIN_ELEMENTS["dialog_ok"], 2000)
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
                lay := root.FindElement({Name: JEWELRY_SOLD_MARGIN_ELEMENTS["layouts_caret"]})
                if lay {
                    emptyGrid := true
                    LogMessage("    [grid] rendered but returned 0 rows — treating as legitimate empty result")
                }
            }
            if (!emptyGrid) {
                LogVisibleNames()
                throw Error("Sold-margin grid did not render within 180s — see diag dump")
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
                throw Error("Failed to walk sold-margin grid (no DataItem rows found)")
            }
            LogMessage("    wrote " . rowsWritten . " data rows to CSV")
            result["row_count"] := rowsWritten
        }

        ; Robust exit: Cancel out of the editor, then confirm Dashboard.
        LogMessage("  step 8: exit editor -> Dashboard")
        Loop 4 {
            try ClickByName(JEWELRY_SOLD_MARGIN_ELEMENTS["panel_cancel"], 2500)
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
            try ClickByName(JEWELRY_SOLD_MARGIN_ELEMENTS["panel_cancel"], 2000)
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
