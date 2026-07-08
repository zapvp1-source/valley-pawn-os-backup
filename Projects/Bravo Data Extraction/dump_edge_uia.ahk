; ============================================================================
; dump_edge_uia.ahk — exhaustive UIA tree dump of the Edge window, walking
; into Document elements where the page DOM lives. Use this to find the
; "Click to Continue" button so we can target it.
; ============================================================================
#Requires AutoHotkey v2.0
#Include lib\UIA-v2\UIA.ahk

global LOG_PATH := A_ScriptDir . "\logs\dump_edge_uia.log"
global INDENT := ""
global MAX_DEPTH := 8
global EMITTED := 0

WriteLog(msg) {
    line := FormatTime(, "yyyy-MM-dd HH:mm:ss") . " " . msg . "`r`n"
    try FileAppend(line, LOG_PATH, "UTF-8")
}

WalkElement(elem, depth) {
    global INDENT, MAX_DEPTH, EMITTED
    if (depth > MAX_DEPTH || EMITTED > 800)
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
    nDisplay := (StrLen(n) > 100) ? SubStr(n, 1, 97) . "..." : n
    if (n != "" || autoId != "") {
        WriteLog(pad . "[" . ct . "] '" . nDisplay . "' (AutoId=" . autoId . ")")
        EMITTED++
    }
    try {
        children := elem.GetChildren()
        for child in children
            WalkElement(child, depth + 1)
    }
}

WriteLog("=== dump_edge_uia start ===")

; Find SSRS Edge window
edgeHwnd := 0
for hwnd in WinGetList("ahk_exe msedge.exe") {
    try {
        t := WinGetTitle("ahk_id " . hwnd)
        if (InStr(t, "Reporting Services") || InStr(t, "Company Performance")) {
            edgeHwnd := hwnd
            WriteLog("SSRS Edge hwnd=" . hwnd . " title='" . t . "'")
            break
        }
    }
}

if !edgeHwnd {
    WriteLog("no SSRS Edge")
    ExitApp(1)
}

WinActivate("ahk_id " . edgeHwnd)
WinWaitActive("ahk_id " . edgeHwnd, , 5)
Sleep(1500)

try {
    root := UIA.ElementFromHandle(edgeHwnd)
    WalkElement(root, 0)
    WriteLog("emitted " . EMITTED . " elements")
} catch as e {
    WriteLog("UIA error: " . e.Message)
}

WriteLog("=== done ===")
ExitApp(0)
