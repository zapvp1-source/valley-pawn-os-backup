#Requires AutoHotkey v2.0
; _bravo_probe.ahk — list visible windows, activate Bravo, report state
out := "Y:\Documents\Claude\Projects\Bravo Data Extraction\logs\_bravo_probe.txt"
try FileDelete(out)
s := ""
for hwnd in WinGetList() {
    title := WinGetTitle(hwnd)
    cls := WinGetClass(hwnd)
    if (title != "")
        s .= hwnd . "|" . cls . "|" . title . "`n"
}
FileAppend(s, out)
if WinExist("ahk_exe Bravo.exe") {
    WinActivate
    WinMaximize
    Sleep 1500
    FileAppend("BravoActive=" . WinGetTitle("A") . "`n", out)
} else {
    FileAppend("NoBravoExeWindow`n", out)
}
ExitApp
