#Requires AutoHotkey v2.0
; _bravo_direct.ahk — launch Bravo.exe directly from the ClickOnce cache (newest build)
out := "Y:\Documents\Claude\Projects\Bravo Data Extraction\logs\_bravo_direct.txt"
try FileDelete(out)
log(msg) {
    global out
    FileAppend(FormatTime(, "HH:mm:ss") . " " . msg . "`n", out)
}

; clear any stuck instances first
while ProcessExist("Bravo.exe") {
    ProcessClose("Bravo.exe")
    Sleep 500
}
log("cleared old instances")
Sleep 1500

exe := "C:\Users\joshuadavis\AppData\Local\Apps\2.0\MKLGKA3Q.J4Q\E6M442AA.RCO\brav..tion_bedf2368dd9fadbc_07ea.0002_c3d2b4e720841eed\Bravo.exe"
dir := "C:\Users\joshuadavis\AppData\Local\Apps\2.0\MKLGKA3Q.J4Q\E6M442AA.RCO\brav..tion_bedf2368dd9fadbc_07ea.0002_c3d2b4e720841eed"
Run('"' . exe . '"', dir)
log("launched direct: " . exe)

loop 36 {
    Sleep 5000
    if WinExist("ahk_exe Bravo.exe") {
        wt := WinGetTitle("ahk_exe Bravo.exe")
        log("bravo window: [" . wt . "]")
        if InStr(wt, "VALLEY") || InStr(wt, "Login") {
            log("READY: " . wt)
            break
        }
    } else {
        log("no bravo window yet (proc=" . (ProcessExist("Bravo.exe") ? "alive" : "dead") . ")")
    }
}
log("done")
ExitApp
