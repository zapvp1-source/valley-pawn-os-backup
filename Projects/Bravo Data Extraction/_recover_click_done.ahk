; One-off recovery: find and click Bravo's "Done" button via UIA to exit a
; stuck Report Preview. Run from inside the VM via prlctl exec.
#Requires AutoHotkey v2.0
SetWorkingDir(A_ScriptDir)
#Include lib\UIA-v2\UIA.ahk

WinActivate("Bravo ahk_class HwndWrapper*")
Sleep(800)

bravoHwnd := WinExist("Bravo ahk_class HwndWrapper*")
if !bravoHwnd {
    FileAppend("ERROR: Bravo window not found`r`n", A_ScriptDir . "\logs\_recover_click_done.log")
    ExitApp(1)
}
root := UIA.ElementFromHandle(bravoHwnd)

candidates := root.FindAll({Name: "Done", Type: "Button"})
FileAppend(FormatTime(, "yyyy-MM-dd HH:mm:ss") . " found " . candidates.Length . " Done buttons`r`n", A_ScriptDir . "\logs\_recover_click_done.log")

clicked := 0
for el in candidates {
    try {
        if el.IsEnabled && el.IsOffscreen = 0 {
            el.Click("left")
            FileAppend("  clicked Done`r`n", A_ScriptDir . "\logs\_recover_click_done.log")
            clicked := 1
            Sleep(2000)
            break
        }
    } catch as e {
        FileAppend("  click attempt error: " . e.Message . "`r`n", A_ScriptDir . "\logs\_recover_click_done.log")
    }
}
if !clicked {
    ; Fallback: send Esc
    Send "{Esc}"
    Sleep(500)
    Send "{Esc}"
    FileAppend("  no Done clickable; sent Esc twice as fallback`r`n", A_ScriptDir . "\logs\_recover_click_done.log")
}

; Then try again — maybe a second Done from the reports-list panel
Sleep(1000)
candidates2 := root.FindAll({Name: "Done", Type: "Button"})
FileAppend("  after first click, " . candidates2.Length . " Done buttons remain`r`n", A_ScriptDir . "\logs\_recover_click_done.log")
for el in candidates2 {
    try {
        if el.IsEnabled && el.IsOffscreen = 0 {
            el.Click("left")
            FileAppend("  clicked second Done`r`n", A_ScriptDir . "\logs\_recover_click_done.log")
            Sleep(1500)
            break
        }
    } catch as e {
    }
}

FileAppend("  recover done`r`n", A_ScriptDir . "\logs\_recover_click_done.log")
ExitApp(0)
