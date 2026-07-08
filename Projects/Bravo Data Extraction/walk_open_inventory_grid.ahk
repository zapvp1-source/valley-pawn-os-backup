; ============================================================================
; walk_open_inventory_grid.ahk
;
; Standalone AHK script — assumes Bravo is currently showing a Custom Report
; list view with DataItem rows. Walks the grid (with PageDown scrolling),
; writes CSV to the user-specified output path. No navigation, no clicks
; on dialogs.
;
; Usage: launch via Session-1 scheduled task. Output is hardcoded below.
; ============================================================================

#Requires AutoHotkey v2.0
#SingleInstance Force

#Include \\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\lib\UIA-v2\UIA.ahk

; Derive store code from Bravo title bar (e.g. "VALLEY PAWN - CULPEPER (CUL)").
; Output filename pattern: {YYYY-MM-DD}_{STORE}_inventory.csv
DeriveStoreCode() {
    try {
        title := WinGetTitle("Bravo ")
        if RegExMatch(title, "VALLEY PAWN - [A-Z]+ \(([A-Z]{3})\)", &m)
            return m[1]
    }
    return "UNKNOWN"
}

STORE_CODE  := DeriveStoreCode()
DATE_STAMP  := FormatTime(, "yyyy-MM-dd")
OUTPUT_PATH := "\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\output\" . DATE_STAMP . "_" . STORE_CODE . "_inventory.csv"
LOG_PATH    := "\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\logs\walk_open_inventory_grid.log"

LogMsg(msg) {
    line := FormatTime(, "yyyy-MM-dd HH:mm:ss") . " " . msg . "`r`n"
    try FileAppend(line, LOG_PATH, "UTF-8-RAW")
}

GetBravoRoot() {
    hwnd := WinExist("Bravo ")
    if !hwnd
        throw Error("Bravo window not found")
    return UIA.ElementFromHandle(hwnd)
}

ToCsvField(v) {
    s := String(v)
    if (InStr(s, ",") || InStr(s, "`"") || InStr(s, "`n") || InStr(s, "`r"))
        return "`"" . StrReplace(s, "`"", "`"`"") . "`""
    return s
}

JoinCsvRow(cells) {
    line := ""
    for i, c in cells {
        if (i > 1)
            line .= ","
        line .= ToCsvField(c)
    }
    return line
}

; Try to find and click a "Show More" / "Load More" pagination button anywhere
; in the Bravo window. Returns true if found and clicked, false otherwise.
TryClickShowMore() {
    candidates := ["Show More", "Show more", "Load More", "Load more", "More Results", "Show all", "Show All", "Next Page", "More"]
    try {
        root := GetBravoRoot()
        for label in candidates {
            try {
                el := root.FindElement({Name: label})
                if el {
                    try {
                        el.InvokePattern.Invoke()
                        LogMsg("  TryClickShowMore: invoked '" . label . "'")
                        return true
                    } catch {
                        try {
                            el.Click("left")
                            LogMsg("  TryClickShowMore: mouse-clicked '" . label . "'")
                            return true
                        }
                    }
                }
            }
        }
    }
    return false
}

WalkGridWithScroll(outputPath) {
    allRows := Map()
    columnAutoIds := []
    columnLabels := Map()
    totalRows := -1
    pagesNoNew := 0
    pageIdx := 0
    maxPages := 500  ; safety: ~10000 rows worth

    ; Wait for grid to render — poll for DataItems up to 180s. Bravo can take
    ; a long time to load 5000+ rows of inventory data.
    LogMsg("waiting for grid to render (poll DataItems up to 180s)...")
    waitDeadline := A_TickCount + 180000
    firstDi := 0
    Loop {
        try {
            root := GetBravoRoot()
            dis := root.FindElements({Type: "DataItem"})
            if (dis && dis.Length > 0) {
                firstDi := dis[1]
                LogMsg("grid rendered with " . dis.Length . " visible rows after " . ((A_TickCount - (waitDeadline - 180000)) // 1000) . "s")
                break
            }
        }
        if (A_TickCount > waitDeadline) {
            LogMsg("WARN: grid never rendered (DataItems never appeared); aborting")
            return -1
        }
        Sleep(3000)
    }
    ; Focus first DataItem
    try {
        firstDi.Click("left")
        Sleep(300)
    }

    Loop maxPages {
        pageIdx++
        dataItems := 0
        try {
            root := GetBravoRoot()
            dataItems := root.FindElements({Type: "DataItem"})
        } catch as e {
            LogMsg("WARN enumerate pass " . pageIdx . ": " . e.Message)
            break
        }
        ; If 0 DataItems mid-walk, don't break — try Show More + retry once.
        ; (PageDown sometimes briefly takes focus off the grid; we recover by
        ; trying Show More which also re-renders the grid.)
        if (allRows.Count > 0 && (!dataItems || dataItems.Length = 0)) {
            LogMsg("pass " . pageIdx . ": 0 DataItems mid-walk, trying Show More + retry")
            clicked := TryClickShowMore()
            if clicked {
                Sleep(2500)
            } else {
                ; Try a click on title bar to re-focus the window then PageUp
                try {
                    WinActivate("Bravo ")
                    Sleep(300)
                    Send("{PgUp}")
                    Sleep(600)
                }
            }
            continue
        }
        if (!dataItems || dataItems.Length = 0) {
            LogMsg("No DataItems on pass " . pageIdx)
            break
        }

        newRows := 0
        for di in dataItems {
            kids := 0
            try kids := di.FindElements({Scope: 2})
            if (!kids || kids.Length = 0)
                continue

            rowIdx := -1
            for k in kids {
                kName := ""
                try kName := k.Name
                if RegExMatch(kName, "Row (\d+) of (\d+)", &m) {
                    rowIdx := Integer(m[1])
                    rt := Integer(m[2])
                    if (totalRows < 0 || rt > totalRows)
                        totalRows := rt
                    break
                }
            }
            if (rowIdx < 0)
                continue
            if (allRows.Has(rowIdx))
                continue

            rowMap := Map()
            for k in kids {
                kAutoId := ""
                kName := ""
                try kAutoId := k.AutomationId
                try kName := k.Name
                if (kAutoId = "")
                    continue
                if (!columnLabels.Has(kAutoId)) {
                    columnAutoIds.Push(kAutoId)
                    lbl := kAutoId
                    if RegExMatch(kName, "Column ([^,]+), Column \d+ of \d+", &mc)
                        lbl := mc[1]
                    columnLabels[kAutoId] := lbl
                }
                v := kName
                colonPos := InStr(kName, ": ", false, -1)
                if (colonPos > 0)
                    v := SubStr(kName, colonPos + 2)
                rowMap[kAutoId] := v
            }
            allRows[rowIdx] := rowMap
            newRows++
        }

        LogMsg("pass " . pageIdx . " new=" . newRows . " seen=" . allRows.Count . "/" . (totalRows > 0 ? totalRows : "?"))

        if (totalRows > 0 && allRows.Count >= totalRows) {
            LogMsg("captured all " . totalRows . " rows")
            break
        }
        ; New rows from this scroll? Keep scrolling.
        if (newRows > 0) {
            pagesNoNew := 0
            Send("{PgDn}")
            Sleep(400)
            continue
        }

        ; Zero-new scroll pass — try Show More first (most likely cause).
        pagesNoNew++
        clicked := TryClickShowMore()
        if (clicked) {
            LogMsg("clicked Show More; waiting for new batch to render")
            Sleep(2500)
            ; Re-focus the LAST visible DataItem so subsequent PageDown scrolls
            ; into the freshly-loaded rows.
            try {
                root := GetBravoRoot()
                dis := root.FindElements({Type: "DataItem"})
                if (dis && dis.Length > 0) {
                    try dis[dis.Length].Click("left")
                    Sleep(300)
                }
            }
            pagesNoNew := 0
            continue
        }

        ; No Show More found — try one more PageDown then give up.
        if (pagesNoNew >= 2) {
            LogMsg("2 zero-new passes + no Show More; stopping at " . allRows.Count)
            break
        }
        Send("{PgDn}")
        Sleep(600)
    }

    if (allRows.Count = 0 || columnAutoIds.Length = 0) {
        LogMsg("ERROR: no rows captured")
        return -1
    }

    ; Write CSV
    try FileDelete(outputPath)
    headerLine := ""
    for i, autoId in columnAutoIds {
        if (i > 1)
            headerLine .= ","
        headerLine .= ToCsvField(columnLabels[autoId])
    }
    FileAppend(headerLine . "`r`n", outputPath, "UTF-8-RAW")
    LogMsg("header: " . headerLine)

    sortedIdx := []
    for idx, _ in allRows
        sortedIdx.Push(idx)
    n := sortedIdx.Length
    i := 2
    while (i <= n) {
        j := i
        while (j > 1 && sortedIdx[j] < sortedIdx[j-1]) {
            tmp := sortedIdx[j]
            sortedIdx[j] := sortedIdx[j-1]
            sortedIdx[j-1] := tmp
            j--
        }
        i++
    }

    count := 0
    for idx in sortedIdx {
        r := allRows[idx]
        rowLine := ""
        for i, autoId in columnAutoIds {
            if (i > 1)
                rowLine .= ","
            v := r.Has(autoId) ? r[autoId] : ""
            rowLine .= ToCsvField(v)
        }
        FileAppend(rowLine . "`r`n", outputPath, "UTF-8-RAW")
        count++
    }
    LogMsg("wrote " . count . " data rows to " . outputPath)
    return count
}

LogMsg("=== walk_open_inventory_grid.ahk started ===")

; Activate Bravo first
try {
    WinActivate("Bravo ")
    WinWaitActive("Bravo ", , 5)
    Sleep(500)
}

rows := WalkGridWithScroll(OUTPUT_PATH)
LogMsg("done; rows=" . rows)
ExitApp(0)
