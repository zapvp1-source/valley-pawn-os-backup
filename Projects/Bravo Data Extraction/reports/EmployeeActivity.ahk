; ============================================================================
; reports/EmployeeActivity.ahk
;
; Pulls Bravo's "Employee Activity" report for a single store with date range
; = (start) to today, exports as CSV.
;
; SKILL it powers: weekly-employee-sales-rankings
;
; UI path:
;   Dashboard -> Reports (sidebar)
;   -> Closing Reports -> Employee Activity (tile)
;   -> Preview (right panel) [or double-click the tile]
;   -> Employee Activity Report Configuration dialog
;       -> Start Date via CALENDAR PICKER (typing is unreliable)
;       -> End Date stays at today
;       -> Ok
;   -> Report Preview renders
;   -> Export... -> Csv -> path -> uncheck open-after -> OK
;   -> Done x2 back to Dashboard
;
; The trigger's `date` field is treated as the Start Date (typically the
; first-of-month for MTD rankings). End date is left at today.
;
; IMPORTANT: Bravo's date field is masked and rejects typed input. We
; SetValueByName which clipboard-pastes via UIA; that's been more reliable
; than triple-click + type. If this still fails, fall back to calendar
; picker walking (TODO: implement if needed).
; ============================================================================

#Requires AutoHotkey v2.0

global EMPACT_ELEMENTS := Map(
    "sidebar_reports",    "Reports",
    "report_tile",        "Employee Activity",
    "config_start_date",  "Start Date",
    "config_end_date",    "End Date",
    "config_ok",          "Ok",
    "preview_export",     "Export...",
    "export_ok",          "OK",
    "panel_done",         "Done"
)

PullEmployeeActivity(store, date, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "employee-activity",
        "store",       store,
        "date",        date,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    outputPath := outputDir . "\" . OutputFilename(date, store, "employee-activity")
    LogMessage("[" . store . "] EmployeeActivity start_date=" . date . " -> " . outputPath)

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

        LogMessage("  step 1: open Reports")
        ClickByName(EMPACT_ELEMENTS["sidebar_reports"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: double-click Employee Activity tile (= Preview)")
        DoubleClickByName(EMPACT_ELEMENTS["report_tile"], 8000)
        Sleep(2500)
        DismissPopups()

        ; Set Start Date via clipboard paste through UIA Value.
        ; Trigger date is YYYY-MM-DD; Bravo wants M/D/YYYY.
        LogMessage("  step 3: set Start Date")
        SetReportDate(EMPACT_ELEMENTS["config_start_date"], date)

        LogMessage("  step 4: click config Ok")
        ClickByName(EMPACT_ELEMENTS["config_ok"], 5000)

        if !FindByName(EMPACT_ELEMENTS["preview_export"], 30000)
            throw Error("Preview did not render within 30s")
        Sleep(500)

        LogMessage("  step 5: click Export Document")
        ClickByName(EMPACT_ELEMENTS["preview_export"], 5000)
        if !FindByName(EMPACT_ELEMENTS["export_ok"], 8000)
            throw Error("Export Document dialog did not appear within 8s")

        Sleep(800)
        SetExportFormatCsv()
        SetExportFilePath(outputPath)
        UncheckOpenAfterExport()
        ClickByName(EMPACT_ELEMENTS["export_ok"], 5000)

        if !WaitForFile(outputPath, 30)
            throw Error("CSV file did not appear at " . outputPath . " within 30s")
        Sleep(500)

        try ClickByName(EMPACT_ELEMENTS["panel_done"], 3000)
        Sleep(800)
        try ClickByName(EMPACT_ELEMENTS["panel_done"], 3000)
        Sleep(800)

    } catch as e {
        LogVisibleNames()
        return Fail(result, started, "UIA click sequence failed: " . e.Message)
    }

    rowCount := CountCsvRows(outputPath)
    result["row_count"]   := rowCount
    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: " . rowCount . " rows, " . result["duration_ms"] . "ms")
    return result
}

; Helper: set a Bravo date input by position.
; Bravo's date inputs register as Edit with Name="BravoDateEdit" (no AutoId
; on the wrapper; inner editor has AutoId=PART_Editor). The "Start Date" is
; the leftmost (smallest X) BravoDateEdit wrapper at the top of the dialog.
;
; Trigger date format is YYYY-MM-DD; Bravo wants M/D/YYYY (e.g. "5/1/2026").
; Strategy:
;   1. Find all Edit elements with Name="BravoDateEdit" and AutomationId=""
;      (the wrappers, not the inner PART_Editor children).
;   2. Sort by BoundingRectangle.l (left X).
;   3. The element at index `position-1` is our target (1=Start, 2=End).
;   4. Get its inner Edit (AutoId=PART_Editor) and set Value via clipboard.
SetReportDate(positionOrName, yyyymmdd) {
    parts := StrSplit(yyyymmdd, "-")
    if (parts.Length != 3) {
        LogMessage("  WARN: malformed date " . yyyymmdd . " — leaving field at default")
        return
    }
    y := parts[1]
    m := Integer(parts[2])
    d := Integer(parts[3])
    bravoDate := m . "/" . d . "/" . y

    ; positionOrName can be "Start Date" (treat as position 1) or a number.
    position := 1
    if IsInteger(positionOrName)
        position := Integer(positionOrName)
    else if (positionOrName = "End Date")
        position := 2

    edit := FindBravoDateEditByPosition(position)
    if !edit {
        LogMessage("  WARN: BravoDateEdit at position " . position . " not found — falling back to Name lookup")
        try {
            SetValueByName("BravoDateEdit", bravoDate, 3000)
            Sleep(150)
            Send("{Tab}")
            return
        } catch as e {
            throw Error("SetReportDate: no BravoDateEdit found at position " . position . " and Name fallback also failed: " . e.Message)
        }
    }
    try {
        edit.Value := bravoDate
        LogMessage("    [date] position=" . position . " set to " . bravoDate . " via ValuePattern")
        Sleep(150)
        Send("{Tab}")
        Sleep(150)
        return
    } catch as e {
        LogMessage("    WARN BravoDateEdit ValuePattern failed: " . e.Message)
    }
    ; Fallback: focus + clipboard paste
    try edit.Focus()
    Sleep(200)
    A_Clipboard := bravoDate
    ClipWait(2)
    Send("^a")
    Sleep(100)
    Send("^v")
    Sleep(200)
    Send("{Tab}")
    Sleep(150)
    LogMessage("    [date] position=" . position . " pasted via clipboard")
}

; Find the BravoDateEdit wrapper Edit element at the given visual position
; (1=leftmost = Start Date, 2=second = End Date, etc.). Returns the inner
; PART_Editor Edit (which is where Value/Focus should be applied), or 0.
FindBravoDateEditByPosition(position) {
    wrappers := []
    try {
        root := GetBravoRoot()
        edits := root.FindElements({Type: "Edit"})
        for e in edits {
            n := ""
            try n := e.Name
            if (n != "BravoDateEdit")
                continue
            ; Skip PART_Editor children (we want the outer wrapper)
            autoId := ""
            try autoId := e.AutomationId
            if (autoId = "PART_Editor")
                continue
            rect := 0
            try rect := e.BoundingRectangle
            if !rect
                continue
            wrappers.Push(Map("elem", e, "x", rect.l))
        }
    } catch as ex {
        LogMessage("    WARN FindBravoDateEditByPosition: " . ex.Message)
        return 0
    }
    ; Sort by x ascending (leftmost first)
    n := wrappers.Length
    if (n = 0)
        return 0
    i := 2
    while (i <= n) {
        j := i
        while (j > 1 && wrappers[j]["x"] < wrappers[j - 1]["x"]) {
            tmp := wrappers[j]
            wrappers[j] := wrappers[j - 1]
            wrappers[j - 1] := tmp
            j--
        }
        i++
    }
    if (position < 1 || position > wrappers.Length) {
        LogMessage("    WARN FindBravoDateEditByPosition: position " . position . " out of range (have " . wrappers.Length . ")")
        return 0
    }
    wrapper := wrappers[position]["elem"]
    LogMessage("    [date] position=" . position . " wrapper at x=" . wrappers[position]["x"])
    ; Return the inner PART_Editor child (where ValuePattern actually works)
    try {
        inner := wrapper.FindElement({Type: "Edit"})
        if inner
            return inner
    }
    return wrapper
}
