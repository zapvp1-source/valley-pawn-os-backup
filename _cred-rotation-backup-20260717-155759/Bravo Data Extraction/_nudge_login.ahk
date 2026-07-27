#Requires AutoHotkey v2.0
#SingleInstance Force
if WinExist("ahk_exe Bravo.exe") {
    WinRestore "ahk_exe Bravo.exe"
    WinActivate "ahk_exe Bravo.exe"
    try WinMaximize "ahk_exe Bravo.exe"
    Sleep 800
    WinActivate "ahk_exe Bravo.exe"
}
Sleep 5000
ExitApp
