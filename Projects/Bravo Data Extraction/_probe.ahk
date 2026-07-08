#Requires AutoHotkey v2.0
SetWorkingDir(A_ScriptDir)
logPath := A_ScriptDir . "\logs\bravo_probe.log"
shotPath := A_ScriptDir . "\logs\bravo_probe.png"

logF := FileOpen(logPath, "w")
logF.WriteLine("=== Bravo probe " . FormatTime(, "yyyy-MM-dd HH:mm:ss") . " ===")

; Enumerate all visible top-level windows
ids := WinGetList()
for hwnd in ids {
    try {
        title := WinGetTitle("ahk_id " . hwnd)
        cls := WinGetClass("ahk_id " . hwnd)
        pid := WinGetPID("ahk_id " . hwnd)
        proc := WinGetProcessName("ahk_id " . hwnd)
        WinGetPos &x, &y, &w, &h, "ahk_id " . hwnd
        if (w > 0 && h > 0)
            logF.WriteLine(Format("hwnd={1} pid={2} proc={3} class={4} pos=({5},{6} {7}x{8}) title={9}", hwnd, pid, proc, cls, x, y, w, h, title))
    } catch as e {
        logF.WriteLine("err: " . e.Message)
    }
}

; Look for Bravo and screenshot it
bravoHwnd := WinExist("ahk_exe Bravo.exe")
logF.WriteLine("Bravo hwnd: " . bravoHwnd)
if (bravoHwnd) {
    bravoTitle := WinGetTitle(bravoHwnd)
    logF.WriteLine("Bravo title: '" . bravoTitle . "'")
    WinActivate(bravoHwnd)
    Sleep 500
    ; Use built-in Snipping via key — but simpler: just log title and let CovWin tell us
}

logF.WriteLine("=== done ===")
logF.Close()
ExitApp

