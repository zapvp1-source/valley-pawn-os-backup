#Requires AutoHotkey v2.0
#SingleInstance Force
; Minimal, dependency-free: activate the Bravo window and send Escape twice
; to dismiss the "Limited Time Offer" marketing popup blocking navigation.
SetTitleMatchMode(2)
DetectHiddenWindows(false)
logf := A_ScriptDir "\logs\_dismiss_promo2.log"
Log(msg) {
    global logf
    try FileAppend(FormatTime(, "yyyy-MM-dd HH:mm:ss") " | " msg "`n", logf)
}
try {
    if WinExist("Bravo") {
        WinActivate("Bravo")
        Sleep(300)
        Log("activated Bravo window")
        Send("{Escape}")
        Sleep(400)
        Send("{Escape}")
        Sleep(400)
        Log("sent Escape x2")
    } else {
        Log("Bravo window not found")
    }
} catch as e {
    Log("EXCEPTION: " . e.Message)
}
Log("done")
ExitApp
