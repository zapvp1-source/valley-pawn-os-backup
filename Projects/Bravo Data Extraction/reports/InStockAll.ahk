; ============================================================================
; reports/InStockAll.ahk  (ADDITIVE, 2026-11-24, Joshua: "know every piece of inventory")
; Cell: instock-all.  Based on: reports/EbayListed.ahk (itself a clone of ActiveInvDetails.ahk).
;
; Full item-level list of everything ON THE SHELF for one store.
; Uses the EXISTING saved report "Claude Active Inv Details" read-only (nothing in Bravo is edited).
;
; Why a new handler instead of active-inv-details:
;   1. The old handler gives up after 120s; a full store takes longer to load (CUL 5/15, 11/19).
;   2. The old row-by-row walk cannot finish a big grid (WAY 8/3: 78 of 2331 rows).
;      This one uses the grid's own copy (click a row, Ctrl+A, Ctrl+C), proven on layaways 10/21,
;      and falls back to the row walk only if the copy comes back short.
;   3. All-or-nothing: if captured rows != the grid's own "Row X of N" total, the cell fails and
;      no file is left behind.
;
; Output: <date>_<STORE>_instock-all.tsv (tab separated, header row first) + .meta (expected/captured)
; ============================================================================

#Requires AutoHotkey v2.0

global INSTOCK_ALL_ELEMENTS := Map(
    "sidebar_inventory",    "Inventory",
    "panel_custom_reports", "Custom Reports",
    "saved_report_value",   "Claude Active Inv Details",
    "panel_cancel",         "Cancel"
)

IsaGridTotal() {
    total := 0
    try {
        root := GetBravoRoot()
        for di in root.FindElements({Type: "DataItem"}) {
            for k in di.FindElements({Scope: 2}) {
                kn := ""
                try kn := k.Name
                if RegExMatch(kn, "Row \d+ of (\d+)", &m) {
                    if (Integer(m[1]) > total)
                        total := Integer(m[1])
                    break
                }
            }
            if (total > 0)
                break
        }
    }
    return total
}

; Click first rendered row, Ctrl+A, Ctrl+C, save clipboard. Returns data lines (header excluded), -1 on failure.
IsaClipDump(path) {
    lines := -1
    try FileDelete(path)
    try {
        root := GetBravoRoot()
        first := root.FindElement({Type: "DataItem"})
        r := first.BoundingRectangle
        CoordMode("Mouse", "Screen")
        Click(r.l + 60, r.t + (r.b - r.t) // 2)
        Sleep(1000)
        prev := ""
        try prev := A_Clipboard
        A_Clipboard := ""
        Send("^a")
        Sleep(2500)
        Send("^c")
        if ClipWait(90) {
            Sleep(1500)
            txt := A_Clipboard
            FileAppend(txt, path, "UTF-8-RAW")
            n := 0
            for ln in StrSplit(Trim(txt, "`r`n"), "`n")
                n++
            lines := n - 1
        } else {
            LogMessage("    [clip] clipboard stayed empty after 90s")
        }
        try A_Clipboard := prev
        Click(r.l + 60, r.t + (r.b - r.t) // 2)
        Sleep(600)
    } catch as e {
        LogMessage("    [clip] error " . e.Message)
    }
    return lines
}

PullInStockAll(store, asOfDate, outputDir) {
    return PullInStockCore(store, asOfDate, outputDir, "Claude Active Inv Details", "instock-all")
}

; 2026-11-27: same pull with the detailed columns (saved report "Claude InStock Detail", layout "Claude Item Master").
PullInStockDetail(store, asOfDate, outputDir) {
    return PullInStockCore(store, asOfDate, outputDir, "Claude InStock Detail", "instock-detail")
}

PullInStockCore(store, asOfDate, outputDir, reportName, slug) {
    started := A_TickCount
    result := Map(
        "report",      slug,
        "store",       store,
        "date",        asOfDate,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    LogMessage("[" . store . "] InStockAll as-of=" . asOfDate)
    outputPath := outputDir . "\" . asOfDate . "_" . store . "_" . slug . ".tsv"
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
        ClickByName(INSTOCK_ALL_ELEMENTS["sidebar_inventory"], 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("  step 2: click Custom Reports")
        ClickByName(INSTOCK_ALL_ELEMENTS["panel_custom_reports"], 5000)
        Sleep(1500)

        LogMessage("  step 3: select saved report '" . reportName . "'")
        if !SelectInventorySavedReport(reportName)
            throw Error("SelectInventorySavedReport: could not select " . reportName)
        Sleep(1000)
        ; verify the report actually loaded (the pick can silently keep the previous report)
        loaded := ""
        try loaded := GetBravoRoot().FindElement({AutomationId: "BoxReportName"}).Value
        LogMessage("    BoxReportName = '" . loaded . "'")
        if (loaded != "" && !InStr(loaded, reportName))
            throw Error("wrong report loaded: " . loaded)

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
        LogMessage("  step 4b: waiting up to 1200s for rows")
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
            if (A_TickCount - t0 > 1200000)
                break
            if (Mod(A_Index, 12) = 0)
                LogMessage("    [grid] still loading, " . ((A_TickCount - t0) // 1000) . "s")
            Sleep(4000)
        }
        if (!gridReady)
            throw Error("Grid did not render within 1200s")
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
            LogMessage("    [clip] still short - falling back to row walk")
            try FileDelete(outputPath)
            captured := WriteBuysGridToCsv(outputPath)
            method := "rowwalk-csv"
        }
        if (captured != expected) {
            try FileDelete(outputPath)
            throw Error("captured " . captured . " of " . expected . " rows - refusing a partial list")
        }
        FileAppend("expected=" . expected . "`r`ncaptured=" . captured . "`r`nmethod=" . method . "`r`n", metaPath, "UTF-8-RAW")
        result["row_count"] := captured

        try ClickByName(INSTOCK_ALL_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        try ClickByName(INSTOCK_ALL_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)

    } catch as e {
        try LogVisibleNames()
        try ClickByName(INSTOCK_ALL_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)
        try ClickByName(INSTOCK_ALL_ELEMENTS["panel_cancel"], 3000)
        return Fail(result, started, "UIA click sequence failed: " . e.Message)
    }

    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: " . result["row_count"] . " rows, " . result["duration_ms"] . "ms")
    return result
}
