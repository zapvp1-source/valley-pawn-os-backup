#Requires AutoHotkey v2.0
#Include lib\UIA-v2\UIA.ahk

logfile := A_ScriptDir . "\logs\dismiss_form_once_" . FormatTime(, "yyyyMMdd_HHmmss") . ".log"
FileAppend("=== dismiss_form_once started " . FormatTime() . "`r`n", logfile, "UTF-8")

bravoWin := WinExist("Bravo ahk_exe Bravo.exe")
if !bravoWin
    bravoWin := WinExist("Bravo")
if !bravoWin {
    FileAppend("no Bravo window found`r`n", logfile, "UTF-8")
    ExitApp
}
WinActivate(bravoWin)
Sleep(500)

try {
    root := UIA.ElementFromHandle(bravoWin)
    cancelEl := root.FindElement({Name: "Cancel"})
    if cancelEl {
        cancelEl.Click("left")
        FileAppend("clicked Cancel`r`n", logfile, "UTF-8")
        Sleep(1500)
        try {
            yesEl := root.FindElement({Name: "Yes"})
            if yesEl {
                yesEl.Click("left")
                FileAppend("clicked Yes`r`n", logfile, "UTF-8")
                Sleep(1000)
            }
        }
    } else {
        FileAppend("no Cancel button found`r`n", logfile, "UTF-8")
    }
} catch as e {
    FileAppend("error: " . e.Message . "`r`n", logfile, "UTF-8")
}

FileAppend("=== done " . FormatTime() . "`r`n", logfile, "UTF-8")
ExitApp
