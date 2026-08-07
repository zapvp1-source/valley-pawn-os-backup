; ============================================================================
; reports/JewelryCaseAudit.ahk
;
; Runs one of Joshua's 5 new "Claude Jewelry Audit - <Category>" saved Custom
; Reports from the Inventory sidebar — current on-hand jewelry snapshot,
; one saved report per category (Rings, Pendants, Earrings, Chains,
; Necklaces), built directly in Bravo by Joshua 2026-08-06.
;
; PURPOSE: Jewelry Count Reconciliation v3 — direct ON-HAND comparison
;   against the manager's physical case count, replacing the sold-only flow
;   comparison (which can't account for scrap/forfeiture/buys/transfers that
;   the manager doesn't count either). On-hand nets all of that out
;   automatically, so this is a straight count-vs-count comparison.
;
; ADDITIVE (Rule #4): NEW file, 5 NEW cells (jewelry-case-rings/pendants/
;   earrings/chains/necklaces). Does not touch JewelryCountAudit.ahk,
;   ActiveInvDetails.ahk, or any existing handler/cell. Cloned from the
;   PROVEN ActiveInvDetails.ahk pull-current-state pattern (same Inventory ->
;   Custom Reports path, no date override, SelectInventorySavedReport per the
;   2026-08-03 inv-select fix) with the shared, truncation-guarded
;   WriteBuysGridToCsv walker. These reports are individually small
;   (one jewelry category per store), so they run well under the
;   silent-truncation danger zone documented 2026-08-03.
;
; Trigger schema (string in "date" field):
;   "YYYY-MM-DD"  — captured as the "as-of" date in the output filename only;
;                   this is a current-state report, no date override is sent.
;
; Output CSV columns: whatever each saved report exports. Column structure
;   is being verified live 2026-08-06 (specifically whether Location is
;   present) — see BRAVO_KNOWN_ISSUES.md for the result once confirmed.
; ============================================================================

#Requires AutoHotkey v2.0

global JEWELRY_CASE_CATEGORY_REPORTS := Map(
    "Rings",     "Claude Jewelry Audit - Rings",
    "Pendants",  "Claude Jewelry Audit - Pendants",
    "Earrings",  "Claude Jewelry Audit - Earrings",
    "Chains",    "Claude Jewelry Audit - Chains",
    "Necklaces", "Claude Jewelry Audit - Necklaces"
)

global JEWELRY_CASE_ELEMENTS := Map(
    "sidebar_inventory",    "Inventory",
    "panel_custom_reports", "Custom Reports",
    "dialog_ok",            "Ok",
    "panel_cancel",         "Cancel",
    "layouts_caret",        "Layouts"
)

; category must be one of the keys in JEWELRY_CASE_CATEGORY_REPORTS above.
PullJewelryCaseAudit(category, store, asOfDate, outputDir) {
    started := A_TickCount
    reportCellName := "jewelry-case-" . StrLower(category)
    result := Map(
        "report",      reportCellName,
        "store",       store,
        "date",        asOfDate,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    global JEWELRY_CASE_CATEGORY_REPORTS
    if !JEWELRY_CASE_CATEGORY_REPORTS.Has(category)
        return Fail(result, started, "Unknown jewelry case category: " . category)
    wantReport := JEWELRY_CASE_CATEGORY_REPORTS[category]

    LogMessage("[" . store . "] JewelryCaseAudit category=" . category . " report='" . wantReport . "' as-of=" . asOfDate)
    outputFileName := asOfDate . "_" . store . "_jewelry-case-" . StrLower(category) . ".csv"
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

    ; Pre-dismiss stuck dialogs (same defense as ActiveInvDetails/BuysFromPublic)
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
        ClickByName(JEWELRY_CASE_ELEMENTS["sidebar_inventory"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: click Custom Reports")
        ClickByName(JEWELRY_CASE_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(1500)

        LogMessage("  step 3: select saved report '" . wantReport . "'")
        if !SelectInventorySavedReport(wantReport)
            throw Error("SelectInventorySavedReport: could not select " . wantReport)
        Sleep(1000)

        ; No date override — this is a current-state (as-of-now) report.
        LogMessage("  step 4: click Ok to run")
        Sleep(2500)
        ActivateBravo()
        Sleep(500)
        try {
            ClickByName("Ok", 5000)
            LogMessage("    clicked Ok by name")
        } catch as okErr {
            Send("{Enter}")
            LogMessage("    Ok not found (" . okErr.Message . ") -- sent {Enter} fallback")
        }
        Sleep(2000)

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
            if (A_TickCount - rendCheckStart > 90000)
                break
            Sleep(2000)
        }
        if (!gridReady) {
            LogVisibleNames()
            throw Error("Grid did not render within 90s after click Ok")
        }
        Sleep(3000)
        DismissPopups()

        LogMessage("  step 5: walk grid rows and write CSV")
        rowsWritten := WriteBuysGridToCsv(outputPath)
        if (rowsWritten < 0) {
            LogVisibleNames()
            throw Error("Failed to walk jewelry-case-" . category . " grid (no DataItem rows found)")
        }
        LogMessage("    wrote " . rowsWritten . " data rows to CSV")
        result["row_count"] := rowsWritten

        try ClickByName(JEWELRY_CASE_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        try ClickByName(JEWELRY_CASE_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        try BackToDashboard()

    } catch as e {
        LogVisibleNames()
        Loop 2 {
            try ClickByName(JEWELRY_CASE_ELEMENTS["panel_cancel"], 2000)
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

; Per-category wrappers so the watcher dispatch table can bind a plain
; function ref (matches the rest of the codebase's one-cell-per-function
; convention rather than relying on .Bind() closures).
PullJewelryCaseRings(store, asOfDate, outputDir)     => PullJewelryCaseAudit("Rings", store, asOfDate, outputDir)
PullJewelryCasePendants(store, asOfDate, outputDir)  => PullJewelryCaseAudit("Pendants", store, asOfDate, outputDir)
PullJewelryCaseEarrings(store, asOfDate, outputDir)  => PullJewelryCaseAudit("Earrings", store, asOfDate, outputDir)
PullJewelryCaseChains(store, asOfDate, outputDir)    => PullJewelryCaseAudit("Chains", store, asOfDate, outputDir)
PullJewelryCaseNecklaces(store, asOfDate, outputDir) => PullJewelryCaseAudit("Necklaces", store, asOfDate, outputDir)
