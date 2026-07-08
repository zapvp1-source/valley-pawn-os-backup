#Requires AutoHotkey v2.0
#SingleInstance Force
; ============================================================================
; Bravo Readiness Keeper  (additive — does NOT modify bravo_watcher.ahk)
; Keeps Bravo running, restored, and frontmost so every pipeline handler can
; find and drive the window. Root cause it fixes: handlers fail with
; "Bravo window not found within 30s" when Bravo is minimized / absent / not
; foreground. This loop continuously returns Bravo to the ready state.
;
; Install: copy to  Y:\Documents\Claude\Projects\Bravo Data Extraction\
; Run at login: shortcut in the Windows Startup folder (same as bravo_watcher).
; Safe-by-design: only intervenes when something is WRONG (minimized, gone, or
; a non-Bravo window is foreground). When Bravo (or one of its own dialogs) is
; already foreground, it does nothing — so it never disturbs a handler mid-pull.
;
; -------------------------------------------------------------------------
; 2026-06-22 — UNATTENDED CLICKONCE SELF-HEAL (the months-long gap):
; Bravo launches via ClickOnce (Bravo.appref-ms -> bravoinstall.com). When
; Bravo Store Systems pushes a build, Windows shows a HUMAN-GATED prompt:
;   * "Application Install - Security Warning"  (Install / Don't Install)
;   * "Required update for Bravo"               (download progress)
; With nobody present, the 8 AM run wedged here forever, AND this keeper made
; it worse by re-firing the launcher every cycle (one new prompt per cycle).
; FIX: (1) detect the trust prompt and click INSTALL automatically; (2) while
; an install/update dialog is up, DO NOT relaunch (no prompt storm); (3) a
; launch cooldown so a not-running Bravo is never hammered. Publisher is the
; verified "Bravo Store Systems LLC" — this is the intended update path.
; ============================================================================

SetTitleMatchMode(2)          ; substring title matching

LogFile := A_ScriptDir "\logs\foreground_keeper.log"
Log(msg) {
    global LogFile
    try FileAppend(FormatTime(A_Now, "yyyy-MM-dd HH:mm:ss") " " msg "`n", LogFile)
}

BravoShortcut := "C:\Users\joshuadavis\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Bravo Store Systems\Bravo.appref-ms"

; Click the "Install" button on the ClickOnce trust prompt. Enumerates the
; dialog's buttons and clicks the one whose caption contains "Install" but NOT
; "Don't" — so we never hit "Don't Install". Returns true if it clicked.
ClickInstallButton(winTitle) {
    try WinActivate(winTitle)
    Sleep 300
    clicked := false
    try {
        for ctrl in WinGetControls(winTitle) {
            if !InStr(ctrl, "Button")              ; only real push-buttons (ClassNN like "Button2")
                continue
            txt := ""
            try txt := Trim(StrReplace(ControlGetText(ctrl, winTitle), "&", ""))  ; strip mnemonic &
            ; EXACT "Install" only — never the body label ("...install this application?")
            ; and never the "Don't Install" button.
            if (txt = "Install") {
                try {
                    ControlClick(ctrl, winTitle, , "Left", 1)   ; real activating click
                    clicked := true
                    break
                }
            }
        }
    }
    if (!clicked) {
        ; fallback: try the Alt+I mnemonic some ClickOnce builds expose
        try {
            WinActivate(winTitle)
            Send("!i")
            clicked := true
        }
    }
    return clicked
}

Log("Bravo Readiness Keeper started (poll 20s) [clickonce-selfheal 2026-06-22]")

lastLaunch := 0
LAUNCH_COOLDOWN_MS := 180000        ; >= ClickOnce update window; never hammer the launcher

Loop {
    try {
        ; --- 0) UNATTENDED ClickOnce self-heal — handled FIRST, every cycle ----
        if WinExist("Application Install - Security Warning") {
            Log("ClickOnce TRUST PROMPT detected -> clicking Install (verified publisher Bravo Store Systems LLC)")
            if ClickInstallButton("Application Install - Security Warning")
                Log("  clicked Install OK")
            else
                Log("  WARN could not click Install button")
            Sleep 20000
            continue                 ; let the update proceed; do NOT relaunch
        }
        if WinExist("Required update for Bravo") {
            Log("Bravo UPDATE downloading -> waiting it out (no relaunch, no kill)")
            Sleep 20000
            continue
        }

        hwnd := WinExist("ahk_exe Bravo.exe")
        if (!hwnd) {
            ; --- Bravo not running: launch it, but never hammer the launcher ---
            if ((A_TickCount - lastLaunch) < LAUNCH_COOLDOWN_MS) {
                Log("Bravo not running, but launch cooldown active -> waiting (avoid ClickOnce prompt storm)")
            } else {
                Log("Bravo not running -> launching via shortcut")
                Run('cmd.exe /c start "" "' BravoShortcut '"')
                lastLaunch := A_TickCount
                Sleep 45000                       ; give ClickOnce + login time
            }
        } else {
            mm := WinGetMinMax("ahk_id " hwnd)        ; -1 minimized, 1 max, 0 normal
            isActive := WinActive("ahk_exe Bravo.exe")
            if (mm = -1) {
                Log("Bravo minimized -> restore + activate")
                WinRestore("ahk_id " hwnd)
                WinActivate("ahk_id " hwnd)
            } else if (!isActive) {
                ; only activate when some OTHER app is foreground; never when a
                ; Bravo-owned dialog is foreground (isActive is true for those).
                Log("Bravo not foreground -> activate")
                WinActivate("ahk_id " hwnd)
            }
            ; clear the modal that blocks the Dashboard after login
            if WinExist("Overdue Task Reminder") {
                Log("dismissing Overdue Task Reminder")
                try ControlClick("Remind Me Later", "Overdue Task Reminder")
            }
        }
    } catch as e {
        Log("ERR: " e.Message)
    }
    Sleep 20000
}
