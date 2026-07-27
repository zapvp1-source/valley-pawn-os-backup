; ============================================================================
; lib/Json.ahk — JSON I/O for trigger files and result files
;
; Pure AHK implementation. No PowerShell shelling. Works against the fixed
; trigger/result schemas this project uses.
;
; Trigger schema (input):
;   {
;     "id": "...",
;     "requested_at": "...",
;     "reports": [
;       {"name": "...", "stores": ["CUL","HAR",...], "date": "YYYY-MM-DD"},
;       ...
;     ]
;   }
;
; Result schema (output): see WriteResult below.
; ============================================================================

#Requires AutoHotkey v2.0

; ----- ReadTrigger -----------------------------------------------------------

ReadTrigger(triggerPath) {
    result := Map()
    result["id"]           := ""
    result["requested_at"] := ""
    result["reports"]      := []

    if !FileExist(triggerPath)
        return result

    text := FileRead(triggerPath, "UTF-8")

    if RegExMatch(text, '"id"\s*:\s*"([^"]*)"', &m)
        result["id"] := m[1]

    if RegExMatch(text, '"requested_at"\s*:\s*"([^"]*)"', &m)
        result["requested_at"] := m[1]

    ; Walk each {...} block that contains a "name" field — those are reports.
    pos := 1
    while RegExMatch(text, '\{[^{}]*"name"\s*:\s*"([^"]*)"[^{}]*\}', &reportMatch, pos) {
        reportText := reportMatch[0]
        report := Map()
        report["name"]   := reportMatch[1]
        report["date"]   := ""
        report["stores"] := []

        if RegExMatch(reportText, '"date"\s*:\s*"([^"]*)"', &dm)
            report["date"] := dm[1]

        if RegExMatch(reportText, '"stores"\s*:\s*\[([^\]]*)\]', &sm) {
            storesText := sm[1]
            pos2 := 1
            while RegExMatch(storesText, '"([^"]*)"', &storeM, pos2) {
                report["stores"].Push(storeM[1])
                pos2 := storeM.Pos + storeM.Len
            }
        }

        result["reports"].Push(report)
        pos := reportMatch.Pos + reportMatch.Len
    }

    return result
}

; ----- WriteResult -----------------------------------------------------------

; Writes a JSON file with the per-trigger result. We hand-build the JSON
; because the schema is fixed and small.
;
; resultMap fields:
;   trigger_id   string
;   started_at   string
;   finished_at  string
;   status       "success" | "partial" | "error"
;   cells        Array of Map (each cell with report/store/date/status/...)
;   errors       Array of strings
WriteResult(resultPath, resultMap) {
    sb := "{`r`n"
    sb .= '  "trigger_id":  ' . JsonString(resultMap.Get("trigger_id", "")) . ",`r`n"
    sb .= '  "started_at":  ' . JsonString(resultMap.Get("started_at", "")) . ",`r`n"
    sb .= '  "finished_at": ' . JsonString(resultMap.Get("finished_at", "")) . ",`r`n"
    sb .= '  "status":      ' . JsonString(resultMap.Get("status", "")) . ",`r`n"

    ; cells
    sb .= '  "cells": ['
    cells := resultMap.Get("cells", [])
    if (cells.Length > 0) {
        sb .= "`r`n"
        for i, cell in cells {
            sb .= "    {"
            sb .= '"report": '      . JsonString(cell.Get("report", ""))      . ", "
            sb .= '"store": '       . JsonString(cell.Get("store", ""))       . ", "
            sb .= '"date": '        . JsonString(cell.Get("date", ""))        . ", "
            sb .= '"status": '      . JsonString(cell.Get("status", ""))      . ", "
            sb .= '"output_path": ' . JsonString(cell.Get("output_path", "")) . ", "
            sb .= '"row_count": '   . cell.Get("row_count", 0)                . ", "
            sb .= '"duration_ms": ' . cell.Get("duration_ms", 0)              . ", "
            sb .= '"error": '       . JsonString(cell.Get("error", ""))
            sb .= "}"
            if (i < cells.Length)
                sb .= ","
            sb .= "`r`n"
        }
        sb .= "  "
    }
    sb .= "],`r`n"

    ; errors
    sb .= '  "errors": ['
    errors := resultMap.Get("errors", [])
    if (errors.Length > 0) {
        sb .= "`r`n"
        for i, err in errors {
            sb .= "    " . JsonString(err)
            if (i < errors.Length)
                sb .= ","
            sb .= "`r`n"
        }
        sb .= "  "
    }
    sb .= "]`r`n"

    sb .= "}`r`n"

    ; Overwrite atomically (delete then write)
    if FileExist(resultPath)
        FileDelete(resultPath)
    FileAppend(sb, resultPath, "UTF-8")
}

; Quote a string for JSON output. Handles \, ", \r, \n, \t.
JsonString(s) {
    if (s = "")
        return '""'
    out := String(s)
    out := StrReplace(out, "\", "\\")
    out := StrReplace(out, '"', '\"')
    out := StrReplace(out, "`r", "\r")
    out := StrReplace(out, "`n", "\n")
    out := StrReplace(out, "`t", "\t")
    return '"' . out . '"'
}
