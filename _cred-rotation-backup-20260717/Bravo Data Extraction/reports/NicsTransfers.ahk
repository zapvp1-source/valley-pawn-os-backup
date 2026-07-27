; ============================================================================
; reports/NicsTransfers.ahk
;
; Runs the "Claude NICS transfers" saved Ad Hoc transaction report for a single
; store across a configurable date range. Exports the full row detail as CSV.
;
; PURPOSE: quantify FFL firearm transfers per store + the revenue we make on
; them. At Valley Pawn an FFL transfer is rung as a firearm SALE with $0.00
; cost, priced at $0.01, sold for $0.00, with a NICS fee charged in the
; transaction (the NICS fee is the revenue). On EOD it shows under
; "Retail Sales (Tax Exempt-Other)". The saved Ad Hoc report "Claude NICS
; transfers" isolates these transactions so we can count them and sum the fee.
;
; UI path (per Preston, 2026-06-16):
;   Dashboard -> Void/View Transactions -> Custom Reports -> Choose Saved Report
;     -> "Claude NICS transfers" -> override Start/End Date -> Update -> Enter -> grid
;
; Trigger schema (string in "date" field):
;   "YYYY-MM-DD"                       — single day
;   "YYYY-MM-DD..YYYY-MM-DD"           — explicit range
;
; Cloned from LowDollarLoans.ahk (the proven saved-Ad-Hoc-report pattern).
; Shared helpers reused: SelectSavedReport, SetReportDate, ClickByName,
; EnsureStore, DismissPopups, BackToDashboard, ParseCountFromTitle,
; WriteBuysGridToCsv (generic grid walker), Fail, ResetOutputFile.
;
; NOTE (smoke-verify): no other handler navigates the "Void/View Transactions"
; module. The sidebar label, the Custom Reports button label, and the
; date-criteria/Update behavior of the transaction report generator are modeled
; on the loan generator and must be confirmed on the first single-store smoke
; run. If the date dialog differs, adjust steps 4-6 only — everything else is
; identical to the loan custom-report handlers.
; ============================================================================

#Requires AutoHotkey v2.0

global NICS_TRANSFERS_ELEMENTS := Map(
    "sidebar_view_void",       "Void/View Transactions",
    "panel_custom_reports",    "Custom Reports",
    "saved_report_combo",      "Choose Saved Report",
    "saved_report_value",      "Claude NICS Transfers",
    "dialog_ok",               "Ok",
    "panel_cancel",            "Cancel"
)

PullNicsTransfers(store, dateOrRange, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "nics-transfers",
        "store",       store,
        "date",        dateOrRange,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    ; --- Parse date range ---------------------------------------------------
    startDate := ""
    endDate := ""
    if InStr(dateOrRange, "..") {
        parts := StrSplit(dateOrRange, "..")
        if (parts.Length != 2)
            return Fail(result, started, "Malformed date range: " . dateOrRange . " (expected YYYY-MM-DD..YYYY-MM-DD)")
        startDate := Trim(parts[1])
        endDate := Trim(parts[2])
    } else {
        startDate := dateOrRange
        endDate := dateOrRange
    }
    LogMessage("[" . store . "] NicsTransfers startDate=" . startDate . " endDate=" . endDate)

    outputFileName := startDate . "_to_" . endDate . "_" . store . "_nics-transfers.csv"
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

    ; Pre-dismiss stuck dialogs (mirrors LowDollarLoans defensive cleanup;
    ; also catches the "Till must be opened" Information modal that has only
    ; an Ok button and won't yield to BackToDashboard's Cancel clicks).
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
            okEl := root.FindElement({AutomationId: "PART_OkDialogButton"})
            if okEl {
                try {
                    okEl.InvokePattern.Invoke()
                    dismissed := true
                    Sleep(900)
                }
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

    ; Exit any open Custom Reports editor via its NAMED "Cancel" button.
    ; The editor loops on "Done", so BackToDashboard alone cannot escape it
    ; (and a stranded editor from a prior failed run also defeats
    ; recover-to-dashboard). Click Cancel up to 4x to back fully out.
    Loop 4 {
        exited := false
        try {
            if ClickByName("Cancel", 1500) {
                LogMessage("    [pre-flight] clicked Cancel to exit Custom Reports editor")
                exited := true
                Sleep(1000)
            }
        }
        if (!exited)
            break
    }
    Sleep(300)

    if !BackToDashboard()
        return Fail(result, started, "BackToDashboard could not return Bravo to Dashboard")
    Sleep(500)
    DismissPopups()

    count := 0
    rowsWritten := 0
    try {
        DismissPopups()
        LogMessage("  step 1: open Void/View Transactions")
        ClickByName(NICS_TRANSFERS_ELEMENTS["sidebar_view_void"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: click Custom Reports")
        ClickByName(NICS_TRANSFERS_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(1500)

        ; step 3: select the saved report. Bravo's "BravoComboBox" controls are
        ; Edit-type with NO AutomationId and a shifting Y, and when opened their
        ; item list lives in a popup at the WINDOW ROOT (not under the combo) —
        ; which is why the shared helper's under-combo / bottom-most approach was
        ; flaky. So: find the combo by its "Choose Saved Report" label, open it,
        ; and select the item from the root. Retry up to 3x; verify BoxReportName.
        LogMessage("  step 3: select 'Claude NICS Transfers' (scan combos for item at root)")
        selOk := false
        Loop 3 {
            attempt := A_Index
            NicsSelectByItemScan("Claude NICS Transfers")
            Sleep(1200)
            loadedName := ""
            try loadedName := IntakeGetLoadedReportName()
            if (loadedName != "" && InStr(loadedName, "Claude NICS Transfers")) {
                LogMessage("    [select] confirmed BoxReportName='" . loadedName . "' on attempt " . attempt)
                selOk := true
                break
            }
            LogMessage("    [select] attempt " . attempt . " not confirmed (BoxReportName='" . loadedName . "') — retrying")
            Sleep(1200)
        }
        if (!selOk) {
            LogVisibleNames()
            throw Error("Could not select 'Claude NICS Transfers' after 3 attempts")
        }
        Sleep(800)

        ; step 3b: set fee type = "NICS Fee". The saved report does NOT persist
        ; the fee type (per Preston) — it blanks each run and must be set, or the
        ; report returns nothing. The fee-type control is the BravoComboBox with
        ; AutomationId "TransactionTypeSelector".
        LogMessage("  step 3b: set fee type 'NICS Fee'")
        fcombo := NicsFindComboByAid("TransactionTypeSelector")
        if fcombo {
            if NicsSelectFromCombo(fcombo, "NICS Fee")
                LogMessage("    [fee] selected 'NICS Fee'")
            else
                LogMessage("    [fee] WARN could not select 'NICS Fee' (see root-item dump)")
        } else {
            LogMessage("    [fee] WARN TransactionTypeSelector control not found")
        }
        Sleep(700)

        ; -- steps 4-5: DATES.
        ; Per Joshua (2026-06-18): the date range is a CALENDAR PICKER and must
        ; NEVER be typed. Bravo's date control paints a typed/ValuePattern value
        ; but rejects the commit, which leaves the bottom "Ok" DISABLED so the
        ; report never runs — that was the root cause of every prior 0-row/"dialog
        ; stayed open" failure. For this proof pass we run the report AS SAVED
        ; (no date override) to confirm rows + the $25 fee column flow end-to-end.
        ; Calendar-picker selection for variable weekly/monthly ranges is the
        ; next step (open the date-edit dropdown, click day cells — no typing).
        LogMessage("  steps 4-5: NOT typing dates (picker only) — running report as-saved this pass")

        ; -- step 6: run via the bottom "Ok" button (per Joshua: select report,
        ; hit Ok at the bottom). IntakeClickOkVerified (shared, from
        ; IntakeDetail.ahk) clicks/invokes Ok up to 5x and verifies the criteria
        ; dialog actually closed (no "New Report" button) before proceeding.
        LogMessage("  step 6: click Ok (bottom, verified) to run report")
        Sleep(1200)
        ActivateBravo()
        IntakeClickOkVerified()

        ; -- step 6b: wait for the list to render. The "Layouts" caret only
        ; appears once the data grid has loaded (same render signal IntakeDetail
        ; uses). No caret within 30s = genuinely empty result -> sentinel CSV.
        LogMessage("  step 6b: waiting for list to render (Layouts caret)")
        if !FindByName("Layouts", 30000) {
            LogMessage("    [empty] no Layouts caret — treating as 0 rows, writing sentinel CSV")
            FileAppend("Transaction Number,Date,Customer,Category,Full Description,NICS Fee,Total`r`n", outputPath, "UTF-8-RAW")
            rowsWritten := 0
        } else {
            Sleep(5000)
            DismissPopups()
            LogMessage("  step 7: walk grid rows and write CSV")
            rowsWritten := WriteIntakeDetailGrid(outputPath)
            if (rowsWritten < 0) {
                LogVisibleNames()
                throw Error("Failed to walk NICS grid (no PART_Content cells found)")
            }
            LogMessage("    wrote " . rowsWritten . " data rows to CSV")
        }

        try ClickByName(NICS_TRANSFERS_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        try ClickByName(NICS_TRANSFERS_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
    } catch as e {
        LogVisibleNames()
        return Fail(result, started, "UIA click sequence failed: " . e.Message)
    }

    result["row_count"]   := rowsWritten
    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: count_from_title=" . count . " rows_written=" . rowsWritten . ", " . result["duration_ms"] . "ms")
    return result
}

; ----------------------------------------------------------------------------
; Helpers for Bravo's Void/View Transactions Custom Reports criteria dialog.
; Its dropdowns are Edit-type controls named "BravoComboBox" (no AutomationId,
; shifting Y). When opened, their item list is a popup at the WINDOW ROOT.
; ----------------------------------------------------------------------------

; Find the BravoComboBox whose row aligns with a given text label (e.g.
; "Choose Saved Report"). Returns the combo element, or 0.
NicsFindComboByLabel(labelName) {
    root := 0
    try root := GetBravoRoot()
    if !root
        return 0
    lblY := -1
    try {
        lbl := root.FindElement({Type: "Text", Name: labelName})
        if lbl
            lblY := lbl.BoundingRectangle.t
    }
    if (lblY < 0) {
        LogMessage("    [combo] label '" . labelName . "' not found")
        return 0
    }
    best := 99999, found := 0
    eds := 0
    try eds := root.FindElements({Type: "Edit"})
    if eds {
        for e in eds {
            nm := ""
            try nm := e.Name
            if (nm != "BravoComboBox")
                continue
            ey := -1
            try ey := e.BoundingRectangle.t
            if (ey < 0)
                continue
            d := Abs(ey - lblY)
            if (d < best) {
                best := d
                found := e
            }
        }
    }
    return found
}

; Scan every BravoComboBox: open it, look for `itemName` in the popup at the
; window root, and select it from whichever combo contains it. Robust to combos
; that have no AutomationId, no label, and shifting position. Returns true if
; the item was found+selected.
NicsSelectByItemScan(itemName) {
    root := 0
    try root := GetBravoRoot()
    if !root
        return false
    eds := 0
    try eds := root.FindElements({Type: "Edit"})
    if !eds
        return false
    ci := 0
    for e in eds {
        nm := ""
        try nm := e.Name
        if (nm != "BravoComboBox")
            continue
        ci += 1
        opened := false
        try {
            e.ExpandCollapsePattern.Expand()
            opened := true
        } catch {
            try {
                e.Click("left")
                opened := true
            }
        }
        Sleep(800)
        r2 := 0
        try r2 := GetBravoRoot()
        item := 0
        if r2 {
            lis := 0
            try lis := r2.FindElements({Type: "ListItem"})
            cnt := (lis ? lis.Length : 0)
            LogMessage("    [scan] combo#" . ci . " opened -> root ListItems=" . cnt)
            if lis {
                for li in lis {
                    ln := ""
                    try ln := li.Name
                    if (ln != "")
                        LogMessage("        item: '" . ln . "'")
                    if (item = 0 && InStr(ln, itemName))
                        item := li
                }
            }
        }
        if item {
            sel := false
            try {
                item.SelectionItemPattern.Select()
                sel := true
            } catch {
                try {
                    item.Click("left")
                    sel := true
                }
            }
            Sleep(800)
            LogMessage("    [scan] selected '" . itemName . "' from combo#" . ci)
            return sel
        }
        try e.ExpandCollapsePattern.Collapse()
        Sleep(250)
    }
    LogMessage("    [scan] '" . itemName . "' not found in any combo (scanned " . ci . ")")
    return false
}

; Find a BravoComboBox by its AutomationId (e.g. "TransactionTypeSelector").
NicsFindComboByAid(aid) {
    root := 0
    try root := GetBravoRoot()
    if !root
        return 0
    eds := 0
    try eds := root.FindElements({Type: "Edit"})
    if eds {
        for e in eds {
            ea := ""
            try ea := e.AutomationId
            if (ea = aid)
                return e
        }
    }
    return 0
}

; Open a combo and select an item by name from the popup at the window root.
; Returns true if the item was found+selected.
NicsSelectFromCombo(combo, itemName) {
    if !combo
        return false
    opened := false
    try {
        combo.ExpandCollapsePattern.Expand()
        opened := true
    } catch {
        try {
            combo.Click("left")
            opened := true
        }
    }
    Sleep(900)
    root := 0
    try root := GetBravoRoot()
    if !root
        return false
    item := 0
    try item := root.FindElement({Type: "ListItem", Name: itemName})
    if !item {
        names := ""
        try {
            lis := root.FindElements({Type: "ListItem"})
            if lis {
                for li in lis {
                    ln := ""
                    try ln := li.Name
                    names .= "[" . ln . "]"
                }
            }
        }
        LogMessage("    [combo] item '" . itemName . "' not found at root; ListItems=" . SubStr(names, 1, 400))
        return false
    }
    sel := false
    try {
        item.SelectionItemPattern.Select()
        sel := true
    } catch {
        try {
            item.Click("left")
            sel := true
        }
    }
    Sleep(800)
    return sel
}
