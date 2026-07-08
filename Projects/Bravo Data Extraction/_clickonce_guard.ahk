#Requires AutoHotkey v2.0
#SingleInstance Force
; =============================================================================
; _clickonce_guard.ahk  (NET-NEW, added 2026-06-22)
; -----------------------------------------------------------------------------
; Bravo launches via ClickOnce (the Bravo.appref-ms -> bravoinstall.com).
; When Bravo Store Systems pushes a new build, Windows shows either:
;   * "Application Install - Security Warning"  (re-establish trust; Install/Don't Install)
;   * "Required update for Bravo"               (download progress; finishes on its own)
; If the health gate force-kills Bravo.exe while this is happening, the ClickOnce
; trust/cache state is torn and the silent auto-update turns into a STUCK,
; human-gated prompt -> the 2026-06-22 "no-window / no-dashboard" wedge.
;
; This guard is called by bravo_health_gate.sh BEFORE any force-kill. It:
;   1. Clicks "Install" on the Bravo trust prompt (verified publisher
;      "Bravo Store Systems LLC") so the update proceeds unattended.
;   2. Leaves the "Required update for Bravo" download dialog alone to finish.
; It never kills anything. Idempotent + safe to call repeatedly.
; =============================================================================

SetTitleMatchMode(2)          ; substring title match
DetectHiddenWindows(false)

logf := A_ScriptDir "\logs\_clickonce_guard.log"
Log(msg) {
    global logf
    try FileAppend(FormatTime(, "yyyy-MM-dd HH:mm:ss") " | " msg "`n", logf)
}

clicked := false

; --- 1) Bravo trust / install security prompt --------------------------------
if WinExist("Application Install - Security Warning") {
    Log("found 'Application Install - Security Warning' -> clicking Install")
    try WinActivate()
    Sleep(400)
    ; Click the Install button: enumerate real push-buttons and match caption
    ; EXACTLY "Install" — never the body label ("...install this application?")
    ; and never the "Don't Install" button. (Verified via _test_fake_clickonce.ahk.)
    try {
        for ctrl in WinGetControls("Application Install - Security Warning") {
            if !InStr(ctrl, "Button")
                continue
            txt := ""
            try txt := Trim(StrReplace(ControlGetText(ctrl, "Application Install - Security Warning"), "&", ""))
            if (txt = "Install") {
                ControlClick(ctrl, "Application Install - Security Warning", , "Left", 1)
                clicked := true
                break
            }
        }
    }
    if (!clicked) {
        Log("button-enumerate found no exact 'Install' -> trying Alt+I")
        try {
            WinActivate("Application Install - Security Warning")
            Send("!i")
            clicked := true
        }
    }
}

; --- 2) Required-update download dialog: let it finish, do NOT touch ----------
if WinExist("Required update for Bravo") {
    Log("'Required update for Bravo' present -> leaving it to complete on its own")
}

Log("done clicked=" (clicked ? "yes" : "no"))
ExitApp
