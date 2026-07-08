#Requires AutoHotkey v2.0
#SingleInstance Off
SetTitleMatchMode(2)
if WinExist("Bravo ") {
    try WinRestore("Bravo ")
    Sleep(500)
    try WinActivate("Bravo ")
    Sleep(500)
    try WinMaximize("Bravo ")
    Sleep(3500)
}
ExitApp
