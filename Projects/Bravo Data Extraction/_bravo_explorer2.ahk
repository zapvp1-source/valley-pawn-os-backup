#Requires AutoHotkey v2.0
; _bravo_explorer2.ahk — launch Bravo via explorer (proven path), watch up to 4 min
out := "Y:\Documents\Claude\Projects\Bravo Data Extraction\logs\_bravo_explorer2.txt"
try FileDelete(out)
log(msg) {
    global out
    FileAppend(FormatTime(, "HH:mm:ss") . " " . msg . "`n", out)
}
Run('explorer.exe "C:\Users\joshuadavis\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Bravo Store Systems\Bravo.appref-ms"')
log("explorer launch issued")
loop 48 {
    Sleep 5000
    bw := WinExist("ahk_exe Bravo.exe")
    titles := ""
    for hwnd in WinGetList() {
        t := WinGetTitle(hwnd)
        if (t != "")
            titles .= "[" . t . "] "
    }
    log("bravoWin=" . (bw ? WinGetTitle(bw) : "none") . " proc=" . (ProcessExist("Bravo.exe") ? "alive" : "no") . " dfsvc=" . (ProcessExist("dfsvc.exe") ? "alive" : "no") . " all=" . titles)
    if (bw && InStr(WinGetTitle(bw), "VALLEY")) {
        log("READY")
        break
    }
}
log("done")
ExitApp
