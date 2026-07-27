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
; ============================================================================

LogFile := A_ScriptDir "\logs\foreground_keeper.log"
Log(msg) {
    global LogFile
    try FileAppend(FormatTime(A_Now, "yyyy-MM-dd HH:mm:ss") " " msg "`n", LogFile)
}

BravoShortcut := "C:\Users\joshuadavis\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Bravo Store Systems\Bravo.appref-ms"

Log("Bravo Readiness Keeper started (poll 20s)")

Loop {
    try {
        hwnd := WinExist("ahk_exe Bravo.exe")
        if (!hwnd) {
            ; --- Bravo not running: launch it (BravoAutoLogin handles login) ---
            Log("Bravo not running -> launching via shortcut")
            Run('cmd.exe /c start "" "' BravoShortcut '"')
            Sleep 45000                       ; give ClickOnce + login time
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
