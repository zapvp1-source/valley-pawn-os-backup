#Requires AutoHotkey v2.0
#SingleInstance Force
; =============================================================================
; _dismiss_bravo_already_running.ahk  (NET-NEW, one-off recovery utility)
; -----------------------------------------------------------------------------
; Clicks "OK" on the "Bravo is already running." dialog that can appear when
; a relaunch races an existing Bravo.exe process (seen 2026-07-18 during
; scrap-refining-gold handler smoke-testing). Companion to the existing
; _clickonce_guard.ahk (which handles trust/update prompts, NOT this dialog).
; Scoped to windows whose title contains "Bravo" so it never touches an
; unrelated dialog elsewhere on the VM. Idempotent, logs every attempt.
; =============================================================================
SetTitleMatchMode(2)
DetectHiddenWindows(false)

logf := A_ScriptDir "\logs\_dismiss_bravo_dialog.log"
Log(msg) {
    global logf
    try FileAppend(FormatTime(, "yyyy-MM-dd HH:mm:ss") " | " msg "`n", logf)
}

clicked := false

; Enumerate all top-level windows and look for one whose title or text
; mentions "already running" alongside "Bravo".
try {
    winList := WinGetList()
    for hwnd in winList {
        title := ""
        try title := WinGetTitle("ahk_id " hwnd)
        if (title = "")
            continue
        if !InStr(title, "Bravo") {
            ; Also check window text for the message even if title is generic
            wtext := ""
            try wtext := WinGetText("ahk_id " hwnd)
            if !InStr(wtext, "already running")
                continue
        }
        Log("candidate window hwnd=" hwnd " title='" title "'")
        try WinActivate("ahk_id " hwnd)
        Sleep(300)
        for ctrl in WinGetControls("ahk_id " hwnd) {
            if !InStr(ctrl, "Button")
                continue
            txt := ""
            try txt := Trim(StrReplace(ControlGetText(ctrl, "ahk_id " hwnd), "&", ""))
            if (txt = "OK") {
                ControlClick(ctrl, "ahk_id " hwnd, , "Left", 1)
                Log("clicked OK on hwnd=" hwnd)
                clicked := true
                break
            }
        }
        if (clicked)
            break
    }
}

Log("done clicked=" (clicked ? "yes" : "no"))
ExitApp
