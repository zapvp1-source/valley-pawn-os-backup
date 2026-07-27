#Requires AutoHotkey v2.0
; _bravo_fix.ahk — close blocking dialogs, kill stuck Bravo splash, relaunch
; from inside Session 1, and watch for the login/main window.
out := "Y:\Documents\Claude\Projects\Bravo Data Extraction\logs\_bravo_fix.txt"
try FileDelete(out)
log(msg) {
    global out
    FileAppend(FormatTime(, "HH:mm:ss") . " " . msg . "`n", out)
}

; 1. Close the "Pick an app" dialog if present
if WinExist("Pick an app") {
    WinClose("Pick an app")
    log("closed Pick-an-app dialog")
    Sleep 1000
}

; 2. Kill stuck Bravo splash + dfsvc
while ProcessExist("Bravo.exe") {
    ProcessClose("Bravo.exe")
    Sleep 500
}
log("Bravo.exe processes cleared")
if ProcessExist("dfsvc.exe") {
    ProcessClose("dfsvc.exe")
    log("dfsvc cleared")
}
Sleep 2000

; 3. Relaunch via appref-ms from inside the user session
Run('"C:\Users\joshuadavis\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Bravo Store Systems\Bravo.appref-ms"')
log("relaunched appref-ms")

; 4. Watch for up to 180s; log window titles every 5s
loop 36 {
    Sleep 5000
    titles := ""
    for hwnd in WinGetList() {
        t := WinGetTitle(hwnd)
        if (t != "" && (InStr(t, "Bravo") || InStr(t, "VALLEY") || InStr(t, "Security") || InStr(t, "Update")))
            titles .= "[" . t . "] "
    }
    log("windows: " . (titles = "" ? "(none bravo-related)" : titles))
    ; done when main app window appears (logged-in title contains VALLEY PAWN, or login form exists)
    if WinExist("ahk_exe Bravo.exe") {
        wt := WinGetTitle("ahk_exe Bravo.exe")
        if InStr(wt, "VALLEY") {
            log("MAIN WINDOW READY: " . wt)
            break
        }
    }
}
log("done")
ExitApp
