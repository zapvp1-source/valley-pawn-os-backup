#Requires AutoHotkey v2.0
#SingleInstance Force
; =============================================================================
; _dismiss_bravo_dialog2.ahk  (NET-NEW, one-off recovery utility)
; -----------------------------------------------------------------------------
; v1 (_dismiss_bravo_dialog.ahk) found the "Bravo is already running" window
; via Win32 title match but found no "OK" among Win32 controls -- confirms
; the dialog is a WPF-rendered button (like the rest of Bravo), not a native
; MessageBox. This version uses the SAME UIA library (lib/Bravo.ahk) the
; production handlers already use to click by accessible Name instead.
; =============================================================================
#Include lib\_secrets.ahk
#Include lib\Json.ahk
#Include lib\Bravo.ahk

logf := A_ScriptDir "\logs\_dismiss_bravo_dialog2.log"
Log(msg) {
    global logf
    try FileAppend(FormatTime(, "yyyy-MM-dd HH:mm:ss") " | " msg "`n", logf)
}

clicked := false
try {
    ActivateBravo()
    Sleep(500)
    LogVisibleNames(60)
    if FindByName("OK", 3000) {
        ClickByName("OK", 3000)
        Log("clicked OK via UIA ClickByName")
        clicked := true
    } else {
        Log("OK not found via UIA either")
    }
} catch as e {
    Log("EXCEPTION: " . e.Message)
}

Log("done clicked=" (clicked ? "yes" : "no"))
ExitApp
