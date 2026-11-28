; ============================================================================
; reports/SoldHistoryAll.ahk  (ADDITIVE, 2026-11-27, Bravo Warehouse: Joshua "we need ALL the data")
; Cell: sold-history.  Based on: reports/InStockAll.ahk (clipboard copy, all-or-nothing).
;
; Every item SOLD in a date range for one store, for history backfill. Uses the EXISTING saved report
; "Claude Sold Inv Details" read-only (nothing in Bravo is edited or saved; dates are overridden in the
; dialog for this run only, the same way sold-discount-detail does it).
;
; Why a new handler instead of sold-discount-detail: that one walks the grid row by row and comes back
; short on windows bigger than a day or two (LEX 5/18-5/31: 135 of 152, 11/27). This one copies the whole
; grid at once and checks the count against the grid's own "Row X of N" total.
;
; Trigger "date": "YYYY-MM-DD..YYYY-MM-DD" (required; a single date means that one day).
; Refuses to run unless BOTH dates were set, the saved report name is confirmed, the copied header has
; the sold columns, and rows < 5000 (the saved report's row cap; use a shorter window instead).
; Output: <from>_to_<to>_<STORE>_sold-history.tsv (tab separated, header first) + .meta
; An empty window writes a header-only file with expected=0.
; ============================================================================

#Requires AutoHotkey v2.0

global SOLD_HISTORY_ELEMENTS := Map(
    "sidebar_inventory",    "Inventory",
    "panel_custom_reports", "Custom Reports",
    "saved_report_value",   "Claude Sold Inv Details",
    "panel_cancel",         "Cancel"
)

PullSoldHistoryAll(store, dateOrRange, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "sold-history",
        "store",       store,
        "date",        dateOrRange,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    startDate := dateOrRange
    endDate := dateOrRange
    if InStr(dateOrRange, "..") {
        parts := StrSplit(dateOrRange, "..")
        if (parts.Length != 2)
            return Fail(result, started, "Malformed date range: " . dateOrRange)
        startDate := Trim(parts[1])
        endDate := Trim(parts[2])
    }
    if !RegExMatch(startDate, "^\d{4}-\d{2}-\d{2}$") || !RegExMatch(endDate, "^\d{4}-\d{2}-\d{2}$")
        return Fail(result, started, "sold-history needs YYYY-MM-DD..YYYY-MM-DD, got: " . dateOrRange)
    LogMessage("[" . store . "] SoldHistoryAll " . startDate . " .. " . endDate)
    outputPath := outputDir . "\" . startDate . "_to_" . endDate . "_" . store . "_sold-history.tsv"
    metaPath := outputPath . ".meta"
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

    try FileDelete(outputPath)
    try FileDelete(metaPath)

    ActivateBravo()
    Loop 4 {
        dismissed := false
        for aid in ["btnCancel", "PART_CancelDialogButton"] {
            try {
                root := GetBravoRoot()
                cancelEl := root.FindElement({AutomationId: aid})
                if cancelEl {
                    try {
                        cancelEl.InvokePattern.Invoke()
                        LogMessage("    [pre-dismiss] Invoked " . aid)
                        dismissed := true
                        Sleep(900)
                    }
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
        LogMessage("  step 1: open Inventory")
        ClickByName(SOLD_HISTORY_ELEMENTS["sidebar_inventory"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: click Custom Reports")
        ClickByName(SOLD_HISTORY_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(1500)

        LogMessage("  step 3: select saved report '" . SOLD_HISTORY_ELEMENTS["saved_report_value"] . "'")
        if !SelectInventorySavedReport(SOLD_HISTORY_ELEMENTS["saved_report_value"])
            throw Error("SelectInventorySavedReport: could not select " . SOLD_HISTORY_ELEMENTS["saved_report_value"])
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
            if (loadedName != "" && InStr(loadedName, SOLD_HISTORY_ELEMENTS["saved_report_value"])) {
                verified := true
                break
            }
            if (A_Index = 1) {
                try SelectInventorySavedReport(SOLD_HISTORY_ELEMENTS["saved_report_value"])
                Sleep(1500)
            }
        }
        if (!verified)
            throw Error("saved report did not load - refusing to run")

        LogMessage("  step 3c: set Date Sold range " . startDate . " .. " . endDate)
        SetReportDate(1, startDate)
        Sleep(400)
        SetReportDate(2, endDate)
        Sleep(400)

        LogMessage("  step 4: click Ok")
        Sleep(2500)
        ActivateBravo()
        Sleep(500)
        try {
            ClickByName("Ok", 5000)
        } catch as okErr {
            Send("{Enter}")
            LogMessage("    Ok not found (" . okErr.Message . ") -- sent {Enter}")
        }
        Sleep(2000)

        ; A full store can take many minutes; Bravo's UI is unreachable while it loads. Wait up to 20 min.
        LogMessage("  step 4b: waiting up to 300s for rows")
        gridReady := false
        t0 := A_TickCount
        Loop {
            try {
                root := GetBravoRoot()
                di := root.FindElements({Type: "DataItem"})
                if (di && di.Length > 0) {
                    LogMessage("    [grid] " . di.Length . " rows on screen after " . ((A_TickCount - t0) // 1000) . "s")
                    gridReady := true
                    break
                }
            }
            if (A_TickCount - t0 > 300000)
                break
            if (Mod(A_Index, 12) = 0)
                LogMessage("    [grid] still loading, " . ((A_TickCount - t0) // 1000) . "s")
            Sleep(4000)
        }
        if (!gridReady) {
            hasSurface := false
            try {
                root := GetBravoRoot()
                if root.FindElement({Name: "Layouts"})
                    hasSurface := true
            }
            if (!hasSurface)
                throw Error("Grid did not render within 300s")
            LogMessage("    report surface present with no rows - empty window")
            FileAppend("Number`tStatus`tCategory`tDescription`tCost`tPrice`tLast Sold Price`tDate`r`n", outputPath, "UTF-8-RAW")
            FileAppend("expected=0`r`ncaptured=0`r`nmethod=empty`r`n", metaPath, "UTF-8-RAW")
            try ClickByName(SOLD_HISTORY_ELEMENTS["panel_cancel"], 3000)
            Sleep(800)
            try ClickByName(SOLD_HISTORY_ELEMENTS["panel_cancel"], 3000)
            result["output_path"] := outputPath
            result["status"]      := "success"
            result["duration_ms"] := A_TickCount - started
            return result
        }
        Sleep(6000)
        DismissPopups()

        expected := 0
        Loop 10 {
            expected := IsaGridTotal()
            if (expected > 0)
                break
            Sleep(2000)
        }
        LogMessage("  step 5: grid reports " . expected . " rows; copying")
        if (expected <= 0)
            throw Error("could not read the grid's row total")
        if (expected >= 5000)
            throw Error("grid reports " . expected . " rows, at the report's 5000 row cap - use a shorter window")

        captured := IsaClipDump(outputPath)
        LogMessage("    [clip] expected=" . expected . " captured=" . captured)
        if (captured != expected) {
            LogMessage("    [clip] short - second attempt")
            Sleep(5000)
            captured := IsaClipDump(outputPath)
            LogMessage("    [clip] expected=" . expected . " captured=" . captured)
        }
        method := "clipboard"
        if (captured != expected) {
            try FileDelete(outputPath)
            throw Error("captured " . captured . " of " . expected . " rows - refusing a partial list")
        }
        hdrLine := ""
        try hdrLine := StrSplit(FileRead(outputPath, "UTF-8"), "`n")[1]
        if !(InStr(hdrLine, "Number") && InStr(hdrLine, "Last Sold Price") && InStr(hdrLine, "Date")) {
            try FileDelete(outputPath)
            throw Error("copied grid is not the sold-details layout (header: " . SubStr(hdrLine, 1, 120) . ")")
        }
        FileAppend("expected=" . expected . "`r`ncaptured=" . captured . "`r`nmethod=" . method . "`r`n", metaPath, "UTF-8-RAW")
        result["row_count"] := captured

        try ClickByName(SOLD_HISTORY_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        try ClickByName(SOLD_HISTORY_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)

    } catch as e {
        try LogVisibleNames()
        try ClickByName(SOLD_HISTORY_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        try ClickByName(SOLD_HISTORY_ELEMENTS["panel_cancel"], 3000)
        return Fail(result, started, "UIA click sequence failed: " . e.Message)
    }

    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: " . result["row_count"] . " rows, " . result["duration_ms"] . "ms")
    return result
}
