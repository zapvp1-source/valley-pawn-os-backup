#Requires AutoHotkey v2.0
#SingleInstance Off
if WinExist("Bravo ahk_class") {
    WinActivate("Bravo ahk_class")
    try WinWaitActive("Bravo ahk_class",, 5)
}
ExitApp
