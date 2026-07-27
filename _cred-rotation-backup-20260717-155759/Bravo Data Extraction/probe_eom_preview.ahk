; ============================================================================
; probe_eom_preview.ahk — when Bravo is showing the End of Month preview,
; dump every named UIA element so we can see exactly what the Export ribbon
; button and CSV menu item are called.
;
; Usage: open End of Month preview in Bravo manually (Reports → End of Month
; → dates → Ok). Then run this script. It writes logs/probe_eom_preview.log
; with the full UIA tree.
; ============================================================================
#Requires AutoHotkey v2.0
#Include lib\UIA-v2\UIA.ahk

global LOG_PATH := A_ScriptDir . "\logs\probe_eom_preview.log"
global EMITTED := 0
global MAX_EMIT := 1500

WriteLog(msg) {
    line := FormatTime(, "yyyy-MM-dd HH:mm:ss") . " " . msg . "`r`n"
    try FileAppend(line, LOG_PATH, "UTF-8")
}

Walk(elem, depth) {
    global EMITTED, MAX_EMIT
    if (EMITTED >= MAX_EMIT || depth > 12)
        return
    pad := ""
    Loop depth
        pad .= "  "
    try {
        n := elem.Name
    } catch {
        n := ""
    }
    try {
        ct := elem.LocalizedControlType
    } catch {
        ct := "?"
    }
    try {
        autoId := elem.AutomationId
    } catch {
        autoId := ""
    }
    nDisplay := (StrLen(n) > 80) ? SubStr(n, 1, 77) . "..." : n
    if (n != "" || autoId != "") {
        WriteLog(pad . "[" . ct . "] '" . nDisplay . "' (AutoId=" . autoId . ")")
        EMITTED++
    }
    try {
        children := elem.GetChildren()
        for child in children
            Walk(child, depth + 1)
    }
}

WriteLog("=== probe_eom_preview start ===")

if !WinExist("Bravo ") {
    WriteLog("Bravo window not found")
    ExitApp(1)
}
hwnd := WinExist("Bravo ")
title := WinGetTitle("ahk_id " . hwnd)
WriteLog("Bravo hwnd=" . hwnd . " title='" . title . "'")

try {
    root := UIA.ElementFromHandle(hwnd)
    Walk(root, 0)
    WriteLog("emitted " . EMITTED . " elements")
} catch as e {
    WriteLog("UIA error: " . e.Message)
}

WriteLog("=== done ===")
ExitApp(0)
