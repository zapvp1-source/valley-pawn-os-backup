; ============================================================================
; reports/ChekkitInactivesV2.ahk — V2.2
;
; FIX: original FindSavedReportCombo picked bottom-most BravoComboBox which
; lands on the LAYOUTS combo in the list view BEHIND the dialog (Object_Layout:
; GUID). The actual 'Choose Saved Report' combo is INSIDE the dialog, just
; below the 'Choose Saved Report' Text label.
;
; V2.2 finds the combo by Y-proximity to the 'Choose Saved Report' label.
; ============================================================================
#Requires AutoHotkey v2.0

global CHEKKIT_V2_ELEMENTS := Map(
    "sidebar_customers",    "Customers",
    "panel_custom_reports", "Custom Reports",
    "saved_report_label",   "Choose Saved Report",
    "saved_report_value",   "Chekkit Inactives",
    "dialog_ok",            "Ok",
    "layouts_caret",        "Layouts",
    "panel_cancel",         "Cancel"
)

PullChekkitInactivesV2(store, date, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "chekkit-inactives-v2",
        "store",       store,
        "date",        date,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    outputPath := outputDir . "\" . OutputFilename(date, store, "chekkit-inactives-v2")
    LogMessage("[" . store . "] ChekkitInactivesV2 date=" . date . " -> " . outputPath)

    if !WaitForBravoReady(30)
        return Fail(result, started, "Bravo window not found/ready within 30s")

    ActivateBravo()
    DismissPopups()

    global CONFIG
    password := CONFIG.Has("bravo.password") ? CONFIG["bravo.password"] : ""
    if !EnsureStore(store, password)
        return Fail(result, started, "EnsureStore failed for " . store)
    LogMessage("  store confirmed: " . store)

    ResetOutputFile(outputPath)

    if !BackToDashboard()
        return Fail(result, started, "BackToDashboard could not return Bravo to Dashboard")
    Sleep(500)
    DismissPopups()

    try {
        DismissPopups()
        LogMessage("  step 1: open Customers")
        ClickByName(CHEKKIT_V2_ELEMENTS["sidebar_customers"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: click Custom Reports in right panel")
        ClickByName(CHEKKIT_V2_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(1500)

        LogMessage("  step 3: select Chekkit Inactives via label-proximity selection")
        if !SelectChekkitSavedReportByLabel(CHEKKIT_V2_ELEMENTS["saved_report_label"], CHEKKIT_V2_ELEMENTS["saved_report_value"])
            throw Error("SelectChekkitSavedReportByLabel: could not select 'Chekkit Inactives'")

        LogMessage("  step 4: click Ok to run saved report")
        ClickByName(CHEKKIT_V2_ELEMENTS["dialog_ok"], 5000)

        if !FindByName(CHEKKIT_V2_ELEMENTS["layouts_caret"], 30000)
            throw Error("Chekkit Inactives list did not render within 30s")
        Sleep(5000)

        ScreenshotToFile("v22_list_view_after_ok")

        LogMessage("  step 5: walk grid rows and write CSV")
        rowsWritten := WriteChekkitGridToCsv(outputPath)
        if (rowsWritten < 0) {
            LogVisibleNames()
            throw Error("Failed to walk Chekkit Inactives grid")
        }
        LogMessage("    wrote " . rowsWritten . " rows to CSV")
        result["row_count"] := rowsWritten

        try ClickByName(CHEKKIT_V2_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        try ClickByName(CHEKKIT_V2_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
    } catch as e {
        ScreenshotToFile("v22_fail_state")
        LogVisibleNames()
        return Fail(result, started, "V2.2 click sequence failed: " . e.Message)
    }

    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: " . result["row_count"] . " rows, " . result["duration_ms"] . "ms")
    return result
}

; ----------------------------------------------------------------------------
; SelectChekkitSavedReportByLabel — find combo by Y-proximity to 'Choose Saved
; Report' label, then use type-ahead + keyboard walk + Enter to select.
; ----------------------------------------------------------------------------
SelectChekkitSavedReportByLabel(labelName, valueName) {
    Loop 3 {
        attempt := A_Index
        LogMessage("    [chek-select] attempt " . attempt)

        combo := FindComboNearLabel(labelName)
        if !combo {
            LogMessage("    [chek-select] could not locate combo near label — sleeping 2s")
            Sleep(2000)
            continue
        }

        ; Open dropdown via mouse-click on arrow (right edge)
        rect := 0
        try rect := combo.BoundingRectangle
        if rect {
            CoordMode "Mouse", "Screen"
            cy := Integer(rect.t + rect.b) // 2
            cx_arrow := Integer(rect.r - 20)
            LogMessage("    [chek-select] dropdown arrow click at (" . cx_arrow . "," . cy . ")")
            MouseClick("Left", cx_arrow, cy)
            Sleep(1500)
        }

        ; Strategy 1 — type-ahead
        LogMessage("    [chek-select] strategy 1 — type-ahead")
        try combo.Focus()
        Sleep(300)
        Loop Parse, valueName {
            Send(A_LoopField)
            Sleep(60)
        }
        Sleep(800)
        try {
            cur := ""
            try cur := combo.Value
            LogMessage("    [chek-select] combo.Value after type-ahead = '" . cur . "'")
            if InStr(cur, valueName) {
                Send("{Enter}")
                Sleep(700)
                LogMessage("    [chek-select] selected via type-ahead + Enter")
                return true
            }
        }

        ; Strategy 2 — try ClickByName the value directly (item may be visible now)
        try {
            ClickByName(valueName, 1500)
            Send("{Enter}")
            Sleep(700)
            LogMessage("    [chek-select] selected via ClickByName + Enter")
            return true
        }

        ; Strategy 3 — Home + 100x Down
        LogMessage("    [chek-select] strategy 3 — Down walk")
        try combo.Focus()
        Sleep(200)
        Send("{Home}")
        Sleep(300)
        Loop 100 {
            try {
                cur := combo.Value
                if InStr(cur, valueName) {
                    Send("{Enter}")
                    Sleep(700)
                    LogMessage("    [chek-select] selected via Down walk after " . A_Index . " Downs")
                    return true
                }
            }
            Send("{Down}")
            Sleep(80)
        }

        LogMessage("    [chek-select] attempt " . attempt . " failed — Esc and retry")
        Send("{Escape}")
        Sleep(800)
    }
    return false
}

; ----------------------------------------------------------------------------
; FindComboNearLabel — find the BravoComboBox whose vertical center is closest
; to the given label Text. Excludes BoxColumns/BoxIsShared/BoxSelectCriteria
; (criteria controls) which are above the saved-report combo in the dialog.
; ----------------------------------------------------------------------------
FindComboNearLabel(labelName) {
    try {
        root := GetBravoRoot()
        ; Find the label Text element
        labelY := -1
        texts := root.FindElements({Type: "Text"})
        for t in texts {
            try {
                if (t.Name = labelName) {
                    rect := 0
                    try rect := t.BoundingRectangle
                    if rect {
                        try labelY := Integer(rect.t + rect.b) // 2
                        break
                    }
                }
            }
        }
        if (labelY = -1) {
            LogMessage("    [combo-find] label '" . labelName . "' not found")
            return 0
        }
        LogMessage("    [combo-find] label '" . labelName . "' at y=" . labelY)

        ; Find all BravoComboBox edits
        bestElem := 0
        bestDist := 99999
        edits := root.FindElements({Type: "Edit"})
        for e in edits {
            n := ""
            try n := e.Name
            if (n != "BravoComboBox")
                continue
            autoId := ""
            try autoId := e.AutomationId
            if (autoId = "BoxColumns" || autoId = "BoxIsShared" || autoId = "BoxSelectCriteria")
                continue
            rect := 0
            try rect := e.BoundingRectangle
            if !rect
                continue
            try {
                ey := Integer(rect.t + rect.b) // 2
                ; Only consider combos AT or BELOW the label (saved-report
                ; combo is positioned just below the label Text).
                if (ey < labelY - 50)
                    continue
                dist := Abs(ey - labelY)
                if (dist < bestDist) {
                    bestDist := dist
                    bestElem := e
                    LogMessage("    [combo-find] candidate at y=" . ey . " dist=" . dist . " autoId='" . autoId . "'")
                }
            }
        }
        if bestElem
            LogMessage("    [combo-find] picked combo with dist=" . bestDist)
        return bestElem
    } catch as e {
        LogMessage("    [combo-find] error: " . e.Message)
        return 0
    }
}

