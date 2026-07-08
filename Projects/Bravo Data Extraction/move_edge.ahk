; move_edge.ahk — move Edge SSRS window to a known position + size and
; make sure it's on top.
#Requires AutoHotkey v2.0

global LOG_PATH := A_ScriptDir . "\logs\move_edge.log"

WriteLog(msg) {
    line := FormatTime(, "yyyy-MM-dd HH:mm:ss") . " " . msg . "`r`n"
    try FileAppend(line, LOG_PATH, "UTF-8")
}

WriteLog("=== move_edge start ===")

; List ALL Edge windows for diagnosis
WriteLog("ALL Edge windows:")
for hwnd in WinGetList("ahk_exe msedge.exe") {
    try {
        t := WinGetTitle("ahk_id " . hwnd)
        WinGetPos(&x, &y, &w, &h, "ahk_id " . hwnd)
        WriteLog("  hwnd=" . hwnd . " pos=(" . x . "," . y . ") size=(" . w . "x" . h . ") title='" . t . "'")
    }
}

; Find SSRS Edge window
edgeHwnd := 0
for hwnd in WinGetList("ahk_exe msedge.exe") {
    try {
        t := WinGetTitle("ahk_id " . hwnd)
        if (InStr(t, "Reporting Services") || InStr(t, "Company Performance")) {
            edgeHwnd := hwnd
            break
        }
    }
}

if !edgeHwnd {
    WriteLog("no SSRS Edge")
    ExitApp(1)
}

; Get the primary monitor size so we move Edge into a visible area
MonitorGetWorkArea(1, &mLeft, &mTop, &mRight, &mBottom)
WriteLog("monitor 1 work area: " . mLeft . "," . mTop . " to " . mRight . "," . mBottom)

; Restore (in case minimized), move to primary monitor's top-left, resize big
try WinRestore("ahk_id " . edgeHwnd)
Sleep(300)
WinMove(mLeft + 50, mTop + 50, (mRight - mLeft) - 100, (mBottom - mTop) - 100, "ahk_id " . edgeHwnd)
Sleep(500)
WinActivate("ahk_id " . edgeHwnd)
Sleep(500)

; Switch to first tab
Send("^1")
Sleep(500)

try {
    t := WinGetTitle("ahk_id " . edgeHwnd)
    WinGetPos(&x, &y, &w, &h, "ahk_id " . edgeHwnd)
    WriteLog("after move: pos=(" . x . "," . y . ") size=(" . w . "x" . h . ") title='" . t . "'")
}

WriteLog("=== done ===")
ExitApp(0)
