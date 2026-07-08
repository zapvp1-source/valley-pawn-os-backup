; ============================================================================
; reports/UIADiscover.ahk
;
; Special "report" that dumps Bravo's current UIA element tree to a log file.
; Use this to discover the Name / AutomationId / ControlType of every clickable
; element on the current Bravo screen, so we can refactor the real report
; modules to use UIA element lookups instead of pixel coordinates.
;
; Trigger payload:
;   { "reports": [{ "name": "uia-discover", "stores": ["HAR"], "date": "..." }] }
;
; The trigger's store is just for routing — the script dumps whichever screen
; Bravo happens to be on right now. Drop multiple discovery triggers in sequence
; (with manual nav between), one per screen of interest:
;   1. Dashboard
;   2. Reports listing
;   3. Safe Register Journal config dialog
;   4. DevExpress Report Preview
;   5. Export Document dialog
;
; Output: appends to <output>/uia-tree-<date>.txt with a timestamped section.
; ============================================================================

#Requires AutoHotkey v2.0
; UIA-v2 is included transitively via lib\Bravo.ahk in the watcher.

PullUiaDiscover(store, date, outputDir) {
    started := A_TickCount
    outputPath := outputDir . "\uia-tree-" . date . ".txt"

    result := Map(
        "report",      "uia-discover",
        "store",       store,
        "date",        date,
        "status",      "error",
        "output_path", outputPath,
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    LogMessage("[" . store . "] UIADiscover -> " . outputPath)

    bravoHwnd := WinExist("Bravo ")
    if !bravoHwnd {
        result["error"] := "Bravo window not found"
        result["duration_ms"] := A_TickCount - started
        return result
    }

    try {
        bravoWin := UIA.ElementFromHandle(bravoHwnd)
    } catch as e {
        result["error"] := "ElementFromHandle failed: " . e.Message
        result["duration_ms"] := A_TickCount - started
        return result
    }

    ; Header
    section := "`r`n=========================================`r`n"
    section .= "Captured: " . FormatTime(, "yyyy-MM-dd HH:mm:ss") . "`r`n"
    section .= "Title: " . WinGetTitle("ahk_id " . bravoHwnd) . "`r`n"
    section .= "=========================================`r`n"

    ; Walk the tree
    try {
        section .= DumpUiaTree(bravoWin, 0)
    } catch as e {
        section .= "ERROR walking tree: " . e.Message . "`r`n"
    }

    ; ADDITIVE (2026-07-03): when the trigger `date` contains "desktop", ALSO
    ; dump the DESKTOP ROOT. DevExpress dropdown popups (e.g. the Company KPIs
    ; "Select Date Range" calendar) render in a SEPARATE top-level HWND that is
    ; NOT a child of the Bravo window, so a Bravo-scoped walk misses them. The
    ; desktop-root walk captures those popups. We also print each element's
    ; BoundingRectangle here so we can calibrate geometry against screen pixels.
    if InStr(date, "desktop") {
        section .= "`r`n----- DESKTOP ROOT (popups included, with rects) -----`r`n"
        try {
            desktop := UIA.GetRootElement()
            section .= DumpUiaTreeRects(desktop, 0, 10)
        } catch as e2 {
            section .= "ERROR walking desktop root: " . e2.Message . "`r`n"
        }
    }

    FileAppend(section, outputPath, "UTF-8")

    result["status"] := "success"
    result["row_count"] := 1
    result["duration_ms"] := A_TickCount - started
    LogMessage("  UIADiscover: appended section to " . outputPath)
    return result
}

; Recursively dump an element and its children. Limit depth to keep the output
; readable; most useful elements live within 6-8 levels of the root.
DumpUiaTree(elem, depth, maxDepth := 8) {
    if (depth > maxDepth)
        return ""

    out := ""
    indent := ""
    loop depth
        indent .= "  "

    try {
        name := elem.Name
    } catch {
        name := ""
    }
    try {
        autoId := elem.AutomationId
    } catch {
        autoId := ""
    }
    try {
        ctrlType := elem.LocalizedType
    } catch {
        ctrlType := ""
    }
    try {
        isEnabled := elem.IsEnabled
    } catch {
        isEnabled := ""
    }
    try {
        isOffScreen := elem.IsOffscreen
    } catch {
        isOffScreen := ""
    }

    ; Only emit a line if there's something useful to see
    if (name != "" or autoId != "" or ctrlType != "") {
        line := indent . "[" . ctrlType . "]"
        if (name != "")    line .= " Name='" . name . "'"
        if (autoId != "")  line .= " AutoId='" . autoId . "'"
        if (!isEnabled)    line .= " (disabled)"
        if (isOffScreen)   line .= " (offscreen)"
        out .= line . "`r`n"
    }

    ; Recurse into children
    try {
        children := elem.GetChildren()
        for child in children {
            out .= DumpUiaTree(child, depth + 1, maxDepth)
        }
    } catch {
    }

    return out
}

; Like DumpUiaTree but ALSO prints BoundingRectangle (l,t,r,b) so we can read
; on-screen pixel positions of popup elements. Used for the desktop-root dump.
DumpUiaTreeRects(elem, depth, maxDepth := 10) {
    if (depth > maxDepth)
        return ""
    out := ""
    indent := ""
    loop depth
        indent .= "  "

    name := "", autoId := "", ctrlType := "", rectStr := ""
    try name := elem.Name
    try autoId := elem.AutomationId
    try ctrlType := elem.LocalizedType
    isOff := ""
    try isOff := elem.IsOffscreen
    try {
        r := elem.BoundingRectangle
        if r
            rectStr := " rect=[" . r.l . "," . r.t . "," . r.r . "," . r.b . "]"
    }

    if (name != "" or autoId != "" or ctrlType != "") {
        line := indent . "[" . ctrlType . "]"
        if (name != "")   line .= " Name='" . name . "'"
        if (autoId != "") line .= " AutoId='" . autoId . "'"
        line .= rectStr
        if (isOff)        line .= " (offscreen)"
        out .= line . "`r`n"
    }

    try {
        for child in elem.GetChildren()
            out .= DumpUiaTreeRects(child, depth + 1, maxDepth)
    } catch {
    }
    return out
}
