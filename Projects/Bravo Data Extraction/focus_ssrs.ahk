; focus_ssrs.ahk — bring the Edge SSRS window to the front so Joshua can
; click the "Click to Continue" button.
#Requires AutoHotkey v2.0

global LOG_PATH := A_ScriptDir . "\logs\focus_ssrs.log"

WriteLog(msg) {
    line := FormatTime(, "yyyy-MM-dd HH:mm:ss") . " " . msg . "`r`n"
    try FileAppend(line, LOG_PATH, "UTF-8")
}

WriteLog("=== focus_ssrs start ===")

edgeHwnd := 0
for hwnd in WinGetList("ahk_exe msedge.exe") {
    try {
        t := WinGetTitle("ahk_id " . hwnd)
        if (InStr(t, "Reporting Services") || InStr(t, "Company Performance") || InStr(t, "Log On")) {
            edgeHwnd := hwnd
            WriteLog("SSRS Edge hwnd=" . hwnd . " title='" . t . "'")
            break
        }
    }
}

if !edgeHwnd {
    WriteLog("no SSRS Edge window found — launching one")
    Run('"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --new-window "https://ssrs.bravoapplication.com:9176/ReportServer/?/Bravo/BRAVO%20Company%20Performance&rs:Command=Render&rs:Format=CSV&rc:parameters=false&StartDate=2026/5/1&EndDate=2026/5/22&IsPawnOn=True"')
    Sleep(8000)
    for hwnd in WinGetList("ahk_exe msedge.exe") {
        try {
            t := WinGetTitle("ahk_id " . hwnd)
            if (InStr(t, "Reporting Services") || InStr(t, "Company Performance")) {
                edgeHwnd := hwnd
                WriteLog("launched SSRS Edge hwnd=" . hwnd . " title='" . t . "'")
                break
            }
        }
    }
}

if !edgeHwnd {
    WriteLog("still no SSRS Edge after launch")
    ExitApp(1)
}

; Restore window if minimized, bring to front
try WinRestore("ahk_id " . edgeHwnd)
WinActivate("ahk_id " . edgeHwnd)
WinWaitActive("ahk_id " . edgeHwnd, , 5)

; If there are multiple tabs, the SSRS one may not be active. Try Ctrl+1
; first (jump to first tab) — most likely the SSRS tab was opened first
; in the new window. If that's wrong, Joshua can click the right tab.
Send("^1")
Sleep(500)

try {
    finalTitle := WinGetTitle("ahk_id " . edgeHwnd)
    WriteLog("activated; current title: '" . finalTitle . "'")
}

WriteLog("=== done ===")
ExitApp(0)
