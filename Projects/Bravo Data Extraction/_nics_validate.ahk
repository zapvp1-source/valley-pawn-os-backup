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

; Stable layout GUID of the "Claude NICS Transfers" saved report. Bravo exposes
; each saved report in the picker by this internal object GUID (its UIA Name),
; NOT by its display text. The report is Shared Company-Wide, so this GUID is
; identical at all 5 stores. (Confirmed via UIA recon 2026-08-11.)
global NICS_SAVED_REPORT_GUID := "ef8daf61-e864-412c-ad3b-16a101ea8330"

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

    ; --- CRITICAL (Bravo rule): exit any open report/editor to a clean Dashboard
    ; BEFORE the store switch. Bravo cannot Lock Session from inside a working
    ; view — it hangs "FREE1 is busy with..." and the store selector renders
    ; wrong (seen: "none of these store row Names matched"). The Custom Reports
    ; editor must be exited via "Cancel" (NOT "Done", which loops). Cancel up to
    ; 4x, then BackToDashboard, so EnsureStore starts from a clean Dashboard.
    ActivateBravo()
    Loop 4 {
        exited := false
        try {
            if ClickByName("Cancel", 1500) {
                LogMessage("    [pre-switch] Cancel to exit report/editor")
                exited := true
                Sleep(1000)
            }
        }
        if (!exited)
            break
    }
    try BackToDashboard()
    Sleep(400)
    DismissPopups()

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
    try ScreenshotToFile("s0-dashboard")

    count := 0
    rowsWritten := 0
    try {
        DismissPopups()
        LogMessage("  step 1: open Void/View Transactions")
        ClickByName(NICS_TRANSFERS_ELEMENTS["sidebar_view_void"], 8000)
        Sleep(1500)
        DismissPopups()
        try ScreenshotToFile("s1-voidview")

        LogMessage("  step 2: click Custom Reports")
        ClickByName(NICS_TRANSFERS_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(2500)
        try ScreenshotToFile("cr-dialog")
        LogMessage("  [shot] captured cr-dialog PNG")

        ; step 3: select the saved report. Bravo's "BravoComboBox" controls are
        ; Edit-type with NO AutomationId and a shifting Y, and when opened their
        ; item list lives in a popup at the WINDOW ROOT (not under the combo) —
        ; which is why the shared helper's under-combo / bottom-most approach was
        ; flaky. So: find the combo by its "Choose Saved Report" label, open it,
        ; and select the item from the root. Retry up to 3x; verify BoxReportName.
        ; step 3: select the saved report. Bravo exposes each saved report's UIA
        ; Name as its bound object string ("Object_Layout: <guid>"), NOT the
        ; display text — which is why every text-name match failed. So target the
        ; one combo whose Value starts "Object_Layout:" (the layout/report picker),
        ; open it, and select the item by the report's stable layout GUID
        ; (Shared Company-Wide => same GUID at every store). Verify via BoxReportName.
        LogMessage("  step 3: select saved report by layout GUID (verified via BoxReportName)")
        selOk := false
        Loop 3 {
            attempt := A_Index
            if NicsSelectSavedReport(NICS_SAVED_REPORT_GUID, "Claude NICS Transfers") {
                LogMessage("    [select] confirmed on attempt " . attempt)
                selOk := true
                break
            }
            LogMessage("    [select] attempt " . attempt . " not confirmed — retrying")
            Sleep(1200)
        }
        if (!selOk) {
            LogVisibleNames()
            throw Error("Could not select 'Claude NICS Transfers' after 3 attempts")
        }
        Sleep(800)

        ; step 3b: (removed) Fee type is now PRE-POPULATED on the saved report by
        ; Joshua (Fee = "NICS Fee", Amount > $5.00), so no fee-type step is needed.
        ; The old code set "NICS Fee" on the WRONG combo (TransactionTypeSelector =
        ; the "Customer Transaction" type, not the fee) — dropping it avoids
        ; corrupting the loaded criteria.

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

; ----------------------------------------------------------------------------
; PRIMARY saved-report selector (proven via 2026-08-11 UIA recon).
; The saved-report picker is the ONE BravoComboBox whose bound Value begins
; "Object_Layout:". Each report list item's UIA Name is ALSO its object string
; ("Object_Layout: <guid>"), never the display text — so we select by the
; report's stable layout GUID and confirm with BoxReportName.
; ----------------------------------------------------------------------------
NicsSelectSavedReport(reportGuid, verifyName) {
    root := 0
    try root := GetBravoRoot()
    if !root
        return false
    ; locate the layout/report combo (unique "Object_Layout:" value); keep a
    ; positional fallback = bottom-most combo inside the dialog (x>700).
    repCombo := 0, bestT := -1, fallback := 0
    eds := 0
    try eds := root.FindElements({Type: "Edit"})
    if eds {
        for e in eds {
            nm := ""
            try nm := e.Name
            if (nm != "BravoComboBox")
                continue
            val := ""
            try val := e.Value
            if (SubStr(val, 1, 14) = "Object_Layout:") {
                repCombo := e
                break
            }
            et := -1, ex := -1
            try et := e.BoundingRectangle.t
            try ex := e.BoundingRectangle.l
            if (ex > 700 && et > bestT) {
                bestT := et
                fallback := e
            }
        }
    }
    if !repCombo
        repCombo := fallback
    if !repCombo {
        LogMessage("    [rep] saved-report (Object_Layout) combo not found")
        return false
    }
    ; open the picker
    try {
        repCombo.ExpandCollapsePattern.Expand()
    } catch {
        try repCombo.Click("left")
    }
    Sleep(1100)
    ; select the target report by its layout GUID
    item := 0
    r2 := 0
    try r2 := GetBravoRoot()
    if r2 {
        lis := 0
        try lis := r2.FindElements({Type: "ListItem"})
        if lis {
            for li in lis {
                ln := ""
                try ln := li.Name
                if (item = 0 && InStr(ln, reportGuid))
                    item := li
            }
        }
    }
    if !item {
        LogMessage("    [rep] report item (guid " . SubStr(reportGuid, 1, 8) . "...) not in open list")
        try repCombo.ExpandCollapsePattern.Collapse()
        return false
    }
    try {
        item.SelectionItemPattern.Select()
    } catch {
        try item.Click("left")
    }
    Sleep(1100)
    ; verify the report actually loaded
    ln := ""
    try ln := IntakeGetLoadedReportName()
    if (ln != "" && InStr(ln, verifyName)) {
        LogMessage("    [rep] loaded '" . ln . "' via layout GUID " . SubStr(reportGuid, 1, 8))
        return true
    }
    LogMessage("    [rep] item selected but BoxReportName='" . ln . "' (want '" . verifyName . "')")
    return false
}

; Select a saved report by KEYBOARD type-ahead: focus each BravoComboBox, type
; the report name (the combo matches/highlights it), press Enter, then verify via
; BoxReportName. Works even when the dropdown items are NOT exposed in the
; accessibility tree — the failure mode that beat the tree-scan approach.
NicsSelectReportKeyboard(reportName) {
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
        try e.Click("left")
        Sleep(500)
        ActivateBravo()
        Sleep(200)
        SendText(reportName)
        Sleep(700)
        Send("{Enter}")
        Sleep(900)
        ln := ""
        try ln := IntakeGetLoadedReportName()
        if (ln != "" && InStr(ln, reportName)) {
            LogMessage("    [kbd] report loaded via type-ahead on combo#" . ci . " (BoxReportName='" . ln . "')")
            return true
        }
        Send("{Escape}")
        Sleep(300)
    }
    LogMessage("    [kbd] type-ahead did not load report (scanned " . ci . " combos)")
    return false
}

; Set the fee type by KEYBOARD type-ahead on the TransactionTypeSelector combo.
NicsSetFeeTypeKeyboard(feeName) {
    fc := NicsFindComboByAid("TransactionTypeSelector")
    if !fc {
        LogMessage("    [kbd-fee] TransactionTypeSelector not found")
        return false
    }
    try fc.Click("left")
    Sleep(500)
    ActivateBravo()
    Sleep(200)
    SendText(feeName)
    Sleep(700)
    Send("{Enter}")
    Sleep(700)
    LogMessage("    [kbd-fee] typed fee type '" . feeName . "'")
    return true
}

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
