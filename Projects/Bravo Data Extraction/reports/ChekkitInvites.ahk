; ============================================================================
; reports/ChekkitInvites.ahk — V6
; Adds explicit Chekkit Invites 2 selection from the saved-report dropdown
; so it works on stores where Bravo hasn't persisted the report yet (HAR,
; LEX, ROA, WAY). Finds the saved-report combo by Y-proximity to BoxReportName
; (the in-dialog combo, not the off-screen Layouts combo).
; ============================================================================
#Requires AutoHotkey v2.0

global CHEKKIT_INVITES_ELEMENTS := Map(
    "sidebar_customers",    "Customers",
    "panel_custom_reports", "Custom Reports",
    "expected_report_name", "Chekkit Invites 2",
    "dialog_ok",            "Ok",
    "layouts_caret",        "Layouts",
    "panel_cancel",         "Cancel"
)

PullChekkitInvites(store, date, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "chekkit-invites",
        "store",       store,
        "date",        date,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    parts := StrSplit(date, "-")
    if (parts.Length != 3)
        return Fail(result, started, "Bad date format: " . date)
    dt := parts[1] . parts[2] . parts[3] . "000000"
    lastMonDt := DateAdd(dt, -7, "Days")
    lastSatDt := DateAdd(dt, -2, "Days")
    lastMon := FormatTime(lastMonDt, "yyyy-MM-dd")
    lastSat := FormatTime(lastSatDt, "yyyy-MM-dd")

    outputPath := outputDir . "\" . OutputFilename(date, store, "chekkit-invites")
    LogMessage("[" . store . "] ChekkitInvites date=" . date . " range=" . lastMon . ".." . lastSat . " -> " . outputPath)

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
        ClickByName(CHEKKIT_INVITES_ELEMENTS["sidebar_customers"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: click Custom Reports")
        ClickByName(CHEKKIT_INVITES_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(3000)

        LogMessage("  step 3: select Chekkit Invites 2 from saved-report dropdown")
        if !SelectInvitesSavedReport(CHEKKIT_INVITES_ELEMENTS["expected_report_name"]) {
            ScreenshotToFile("invites_select_fail")
            LogMessage("    WARN: saved-report selection failed; proceeding with whatever is loaded")
        }
        Sleep(1500)

        LogMessage("  step 4a: set First Time In start = " . lastMon)
        try {
            SetReportDate(1, lastMon)
        } catch as e {
            LogMessage("    WARN SetReportDate(1) failed: " . e.Message)
        }
        LogMessage("  step 4b: set First Time In end = " . lastSat)
        try {
            SetReportDate(2, lastSat)
        } catch as e {
            LogMessage("    WARN SetReportDate(2) failed: " . e.Message)
        }
        Sleep(500)

        LogMessage("  step 5: click Ok to run report")
        try ClickByName(CHEKKIT_INVITES_ELEMENTS["dialog_ok"], 5000)

        if !FindByName(CHEKKIT_INVITES_ELEMENTS["layouts_caret"], 30000)
            throw Error("List did not render within 30s")
        Sleep(5000)

        ScreenshotToFile("invites_list_view")

        LogMessage("  step 6: walk grid and write CSV")
        rowsWritten := WriteChekkitInvitesGridToCsv(outputPath)
        if (rowsWritten < 0) {
            LogVisibleNames()
            throw Error("Failed to walk Chekkit Invites grid")
        }
        LogMessage("    wrote " . rowsWritten . " rows to CSV")
        result["row_count"] := rowsWritten

        try ClickByName(CHEKKIT_INVITES_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        try ClickByName(CHEKKIT_INVITES_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
    } catch as e {
        ScreenshotToFile("invites_fail")
        LogVisibleNames()
        return Fail(result, started, "ChekkitInvites failed: " . e.Message)
    }

    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: " . result["row_count"] . " rows, " . result["duration_ms"] . "ms")
    return result
}

; ----------------------------------------------------------------------------
; SelectInvitesSavedReport — find the saved-report combo (the one in the
; dialog, NOT the Layouts combo at y>1500 in the list view behind), open it,
; type the report name, press Enter to commit.
; ----------------------------------------------------------------------------
SelectInvitesSavedReport(valueName) {
    combo := FindInDialogSavedReportCombo()
    if !combo {
        LogMessage("    [invites-select] could not locate in-dialog saved-report combo")
        return false
    }
    rect := 0
    try rect := combo.BoundingRectangle
    if rect {
        cy := Integer(rect.t + rect.b) // 2
        cx := Integer(rect.r - 20)
        LogMessage("    [invites-select] clicking combo arrow at (" . cx . "," . cy . ")")
        MouseClick("Left", cx, cy)
        Sleep(1500)
    }
    LogMessage("    [invites-select] type-ahead: '" . valueName . "'")
    try combo.Focus()
    Sleep(300)
    Loop Parse, valueName {
        Send(A_LoopField)
        Sleep(60)
    }
    Sleep(900)
    Send("{Enter}")
    Sleep(900)
    LogMessage("    [invites-select] Enter pressed")
    return true
}

; Find the saved-report combo by Y-proximity to BoxReportName. The dialog has
; BoxReportName at the top, then the saved-report combo just below it. We
; restrict to BravoComboBoxes whose Y is within 250px of BoxReportName, which
; excludes the Layouts combo at y>1500 from the list view behind.
FindInDialogSavedReportCombo() {
    try {
        root := GetBravoRoot()
        boxY := -1
        edits := root.FindElements({Type: "Edit"})
        for e in edits {
            try {
                autoId := ""
                try autoId := e.AutomationId
                if (autoId != "BoxReportName")
                    continue
                rect := 0
                try rect := e.BoundingRectangle
                if !rect
                    continue
                boxY := Integer(rect.t + rect.b) // 2
                break
            }
        }
        if (boxY = -1) {
            LogMessage("    [combo-find] BoxReportName not located")
            return 0
        }
        LogMessage("    [combo-find] BoxReportName at y=" . boxY)
        bestElem := 0
        bestDist := 99999
        for e in edits {
            try {
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
                ey := Integer(rect.t + rect.b) // 2
                ; Must be BELOW BoxReportName and within 250 px
                if (ey < boxY)
                    continue
                if (ey > boxY + 250)
                    continue
                dist := Abs(ey - boxY)
                if (dist < bestDist) {
                    bestDist := dist
                    bestElem := e
                    LogMessage("    [combo-find] candidate y=" . ey . " dist=" . dist)
                }
            }
        }
        if bestElem
            LogMessage("    [combo-find] picked combo dist=" . bestDist)
        return bestElem
    } catch as e {
        LogMessage("    [combo-find] error: " . e.Message)
        return 0
    }
}

WriteChekkitInvitesGridToCsv(outputPath) {
    cells := []
    try {
        root := GetBravoRoot()
        edits := root.FindElements({Type: "Edit"})
        for e in edits {
            try {
                n := ""
                try n := e.Name
                if (n != "TextEdit")
                    continue
                autoId := ""
                try autoId := e.AutomationId
                if (autoId = "PART_Editor")
                    continue
                rect := 0
                try rect := e.BoundingRectangle
                if !rect
                    continue
                val := ""
                try val := e.Value
                if (val = "")
                    continue
                yVal := 0
                xVal := 0
                try yVal := rect.t
                try xVal := rect.l
                cells.Push(Map("val", val, "x", xVal, "y", yVal))
            }
        }
    } catch as ex {
        LogMessage("    WARN WriteChekkitInvitesGridToCsv: " . ex.Message)
        return -1
    }
    LogMessage("    [invites-walk] found " . cells.Length . " TextEdit data cells")
    if (cells.Length = 0)
        return 0
    n := cells.Length
    i := 2
    while (i <= n) {
        j := i
        while (j > 1) {
            a := cells[j]
            b := cells[j - 1]
            if (a["y"] < b["y"] || (a["y"] = b["y"] && a["x"] < b["x"])) {
                cells[j] := b
                cells[j - 1] := a
                j--
            } else {
                break
            }
        }
        i++
    }
    rows := []
    currentRow := []
    currentY := -9999
    yTolerance := 12
    for c in cells {
        if (Abs(c["y"] - currentY) > yTolerance) {
            if (currentRow.Length > 0)
                rows.Push(currentRow)
            currentRow := []
            currentY := c["y"]
        }
        currentRow.Push(c["val"])
    }
    if (currentRow.Length > 0)
        rows.Push(currentRow)
    LogMessage("    [invites-walk] grouped into " . rows.Length . " rows")
    FileAppend("first_name,last_name,phone,email,dnt,last_visit`r`n", outputPath, "UTF-8-RAW")
    count := 0
    for r in rows {
        phone := ""
        email := ""
        isDnt := false
        for cell in r {
            c := Trim(cell)
            if (c = "")
                continue
            if (InStr(c, "@")) {
                if (email = "")
                    email := c
                continue
            }
            if (c = "DNT") {
                isDnt := true
                continue
            }
            if ((SubStr(c, 1, 1) = "(" || SubStr(c, 1, 4) = "+1-(") && InStr(c, "-")) {
                if (phone = "")
                    phone := c
                continue
            }
        }
        if (phone = "" && email = "")
            continue
        WriteCsvRow(outputPath, "", "", phone, email, isDnt ? "DNT" : "", "")
        count++
    }
    return count
}
