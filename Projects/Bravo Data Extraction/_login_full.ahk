#Requires AutoHotkey v2.0
#SingleInstance Off
SetTitleMatchMode(2)
if !WinExist("Bravo ahk_class")
    ExitApp
Loop 6 {
    WinActivate("Bravo ahk_class")
    Sleep(500)
    if WinActive("Bravo ahk_class")
        break
}
Sleep(1200)
Send("{Tab 10}")
Sleep(150)
Send("+{Tab 5}")
Sleep(150)
Send("^a")
Sleep(100)
Send("FREE1@WAY")
Sleep(300)
Send("{Tab}")
Sleep(150)
Send("Health2035!")
Sleep(300)
Send("{Enter}")
ExitApp
