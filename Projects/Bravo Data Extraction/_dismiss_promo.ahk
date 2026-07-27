#Requires AutoHotkey v2.0
#SingleInstance Force
; =============================================================================
; _dismiss_promo.ahk  (NET-NEW, one-off recovery utility)
; -----------------------------------------------------------------------------
; Bravo occasionally shows a "BRAVO STORE SYSTEMS - LIMITED TIME OFFER"
; marketing popup that BackToDashboard's existing dismiss logic (Cancel/Done)
; does not recognize, wedging navigation (seen 2026-07-18 during
; scrap-refining-gold smoke-testing). This script tries several common
; close patterns via UIA Name match, then falls back to Escape.
; =============================================================================
#Include lib\_secrets.ahk
#Include lib\Json.ahk
#Include lib\Bravo.ahk

logf := A_ScriptDir "\logs\_dismiss_promo.log"
Log(msg) {
    global logf
    try FileAppend(FormatTime(, "yyyy-MM-dd HH:mm:ss") " | " msg "`n", logf)
}

clicked := false
try {
    ActivateBravo()
    Sleep(400)
    LogVisibleNames(150)

    candidates := ["Close", "X", "Dismiss", "No Thanks", "No thanks", "Maybe Later",
                   "Skip", "Not Now", "Cancel", "Done", "Got It", "Got it", "OK", "Ok"]
    for name in candidates {
        if FindByName(name, 1500) {
            try {
                ClickByName(name, 1500)
                Log("clicked '" . name . "'")
                clicked := true
                Sleep(500)
                break
            }
        }
    }

    if (!clicked) {
        Log("no named close control found -> trying Escape x2")
        Send("{Escape}")
        Sleep(400)
        Send("{Escape}")
        Sleep(400)
    }

    Sleep(500)
    LogMessage("    [post-dismiss] re-checking visible names")
    LogVisibleNames(60)
} catch as e {
    Log("EXCEPTION: " . e.Message)
}

Log("done clicked=" (clicked ? "yes" : "no"))
ExitApp
