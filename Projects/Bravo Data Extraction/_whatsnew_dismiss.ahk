#Requires AutoHotkey v2.0
#SingleInstance Force
; _whatsnew_dismiss.ahk — close Bravo's "What's New in Bravo" panel (2026.10.0.85, since 10/28). Additive 2026-10-30.
global WN_LOGFILE := A_ScriptDir . "\logs\_whatsnew.log"
L(m) {
    global WN_LOGFILE
    FileAppend(FormatTime(, "yyyy-MM-dd HH:mm:ss") . " " . m . "`n", WN_LOGFILE)
}
L("=== start")
#Include %A_ScriptDir%\lib\UIA-v2\UIA.ahk
Main()
ExitApp()

Main() {
    hwnd := WinExist("Bravo ")
    if !hwnd {
        L("no Bravo window")
        L("=== end")
        return
    }
    root := UIA.ElementFromHandle(hwnd)
    btns := []
    try btns := root.FindElements({Type: "Button"})
    L("buttons: " . btns.Length)
    for b in btns {
        n := "", id := ""
        try n := b.Name
        try id := b.AutomationId
        try {
            r := b.BoundingRectangle
            L("btn name=[" . n . "] id=[" . id . "] rect=" . r.l . "," . r.t . "," . r.r . "," . r.b)
        }
    }
    clicked := false
    for b in btns {
        n := "", id := ""
        try n := b.Name
        try id := b.AutomationId
        if (id = "Close" || id = "Minimize-Restore" || id = "Maximize-Restore")
            continue   ; NEVER touch the Bravo window controls
        if RegExMatch(n . " " . id, "i)(got it|dismiss|don.?t show|WhatsNew|btnCloseWhatsNew)") {
            try {
                b.Click()
                L("clicked [" . n . "] id=[" . id . "]")
                clicked := true
                Sleep(1500)
                break
            }
        }
    }
    if !clicked {
        WinActivate("ahk_id " . hwnd)
        Sleep(300)
        Send("{Escape}")
        Sleep(1000)
        L("no close button matched; sent Escape")
    }
    still := 0
    try still := root.FindElement({Name: "What's New in Bravo"})
    L("panel still present after: " . (still ? "YES" : "no"))
    L("=== end")
}
