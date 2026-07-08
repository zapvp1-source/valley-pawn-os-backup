; ============================================================================
; click_continue.ahk v2 — click in the Edge page body to give it focus, then
; Tab through to the "Click to Continue" button and press Enter. Watch the
; title to see what happens.
; ============================================================================
#Requires AutoHotkey v2.0

global LOG_PATH := A_ScriptDir . "\logs\click_continue.log"

WriteLog(msg) {
    line := FormatTime(, "yyyy-MM-dd HH:mm:ss") . " " . msg . "`r`n"
    try FileAppend(line, LOG_PATH, "UTF-8")
}

WriteLog("=== click_continue v2 start ===")

; Find Edge SSRS window
edgeHwnd := 0
for hwnd in WinGetList("ahk_exe msedge.exe") {
    try {
        t := WinGetTitle("ahk_id " . hwnd)
        if (InStr(t, "Reporting Services") || InStr(t, "Company Performance") || InStr(t, "Log On")) {
            edgeHwnd := hwnd
            WriteLog("found SSRS Edge hwnd=" . hwnd . " title='" . t . "'")
            break
        }
    }
}

if !edgeHwnd {
    WriteLog("no SSRS Edge window")
    ExitApp(1)
}

WinActivate("ahk_id " . edgeHwnd)
WinWaitActive("ahk_id " . edgeHwnd, , 5)
Sleep(1000)

; Get the window rect and click in the middle of the page body.
; Edge's address bar is at the top ~140px; page body starts below.
WinGetPos(&wx, &wy, &ww, &wh, "ahk_id " . edgeHwnd)
clickX := wx + ww // 2
clickY := wy + 300  ; well below address bar, in the page body
WriteLog("clicking page body at (" . clickX . "," . clickY . ")")
CoordMode("Mouse", "Screen")
Click(clickX, clickY)
Sleep(500)

; The SSRS Forms login page has: TxtUser (pre-filled "reportuser"), TxtPwd
; (empty), BtnLogon ("Click to Continue"). Tab walks through these. After
; clicking in the page body, focus should be near the top — Tab takes us
; to the next interactive element.
;
; Strategy: Tab 5 times (covers a few extra tab stops) then Enter to submit.
; Then check title.
WriteLog("sending Tab Tab Tab Tab Tab Enter")
Send("{Tab 5}")
Sleep(300)
Send("{Enter}")
Sleep(500)

; Wait for navigation
Sleep(5000)

try {
    newTitle := WinGetTitle("ahk_id " . edgeHwnd)
    WriteLog("post-Tab-Enter title: '" . newTitle . "'")
}

; Check downloads
WriteLog("checking Downloads:")
downloadsDir := "C:\Users\joshuadavis\Downloads"
foundCsv := false
loop files, downloadsDir . "\*", "F" {
    WriteLog("  " . A_LoopFileName . " (" . A_LoopFileSize . " bytes)")
    if (InStr(A_LoopFileName, ".csv"))
        foundCsv := true
}
WriteLog("CSV in Downloads: " . (foundCsv ? "YES" : "NO"))

WriteLog("=== done ===")
ExitApp(0)
