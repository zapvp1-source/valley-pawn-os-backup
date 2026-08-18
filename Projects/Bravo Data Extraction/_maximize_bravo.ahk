; _maximize_bravo.ahk — force the Bravo window to fill the guest desktop.
; Added 2026-08-16: after _relaunch_bravo_and_watcher.ps1, Bravo came back
; restored-size and _nudge_login.ahk's plain WinMaximize didn't stick,
; breaking every geometry assumption in the report handlers. This does
; Restore -> Activate -> WinMove full-desktop -> WinMaximize and logs the
; guest resolution for diagnosis.
#Requires AutoHotkey v2.0
#SingleInstance Force
logPath := "Y:\Documents\Claude\Projects\Bravo Data Extraction\logs\maximize_bravo.log"
; Target the MAIN Bravo window by TITLE ("Bravo " — same match _check_reports.ahk
; and _render_bravo.ahk use). ahk_exe Bravo.exe alone can land on a tiny helper
; window (observed 567x71 at 3067,288 on 2026-08-16).
target := WinExist("Bravo ") ? "Bravo " : "ahk_exe Bravo.exe"
if WinExist(target) {
    WinRestore target
    WinActivate target
    Sleep 500
    try WinMove(0, 0, A_ScreenWidth, A_ScreenHeight, target)
    Sleep 500
    try WinMaximize target
    Sleep 500
    x := 0, y := 0, w := 0, h := 0
    try WinGetPos(&x, &y, &w, &h, target)
    try FileAppend(FormatTime(, "yyyy-MM-dd HH:mm:ss") . " target='" . target . "' screen=" . A_ScreenWidth . "x" . A_ScreenHeight . " bravo=" . w . "x" . h . " at " . x . "," . y . "`n", logPath)
} else {
    try FileAppend(FormatTime(, "yyyy-MM-dd HH:mm:ss") . " Bravo window not found`n", logPath)
}
Sleep 1000
ExitApp
