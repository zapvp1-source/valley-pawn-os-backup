; ============================================================================
; bravo_state_guard.ahk  —  Bravo self-healing recovery ladder
;
; PURPOSE: bring Bravo back to a healthy, logged-in store Dashboard from ANY
; state, so the next pipeline trigger starts clean. Fills the gap the existing
; self-heal left open:
;   - _watchdog.ps1 only heals the WATCHER PROCESS (dead / hung queue).
;   - _selfheal.ahk only handled launch + login, not ad popups / modals /
;     "Not Responding" / limbo / force-relaunch.
; This script handles every Bravo UI situation we have seen, escalating from
; cheap to heavy. It reuses the hardened helpers in lib/Bravo.ahk (no copies).
;
; INVOCATION: run in joshuadavis's interactive Session 1 (so it can drive the
; GUI). Normally fired by _bravo_guard_watchdog.ps1, which only calls it when
; the watcher is IDLE (no fresh log activity) — so it never collides with an
; active report run. Can also be run on demand for recovery.
;
; RESULT: writes logs\bravo_guard_result.txt with one of:
;   OK:<store>            already / now on a Dashboard
;   FAIL_UNRECOVERABLE    full ladder exhausted — human alert needed
; and a timestamped detail log at logs\bravo_guard_<date>.log
;
; RECOVERY LADDER (re-evaluated each loop, max passes capped):
;   0. No Bravo window            -> launch via .appref-ms, wait for window
;   1. Window "Not Responding"    -> graceful close, else force-kill, relaunch
;   2. Ad popup / modal up         -> click Close / Remind Me Later / Ok / Cancel
;   3. Login screen / session list -> RecoverFromAutoLock(password)
;   4. On a Dashboard              -> DONE (OK)
;   5. Working view (store code)   -> BackToDashboard
;   6. Limbo (no code, responsive) -> BackToDashboard; if it persists, relaunch
; ============================================================================

#Requires AutoHotkey v2.0
SetWorkingDir(A_ScriptDir)
#Include lib\Json.ahk
#Include lib\Bravo.ahk

global BRAVO_APPREF := "C:\Users\joshuadavis\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Bravo Store Systems\Bravo.appref-ms"
global GUARD_RESULT := A_ScriptDir . "\logs\bravo_guard_result.txt"

; boot marker (direct write, independent of LogMessage) — diagnostic
try FileAppend("BOOT1 " . FormatTime(, "yyyy-MM-dd HH:mm:ss") . " dir=" . A_ScriptDir . "`n", A_ScriptDir . "\logs\bravo_guard_boot.txt", "UTF-8")

InitLog(A_ScriptDir . "\logs", "bravo_guard_" . FormatTime(, "yyyy-MM-dd"))
LogMessage("=== bravo_state_guard start " . FormatTime(, "yyyy-MM-dd HH:mm:ss") . " ===")

; --- credentials from config.json (same source the watcher uses) ----------
password := ""
username := ""
try {
    cfgFile := FileRead(A_ScriptDir . "\config.json")
    cfg := Json.Load(&cfgFile)
    username := cfg["bravo"]["username"]
    password := cfg["bravo"]["password"]
} catch as e {
    LogMessage("  WARN: could not read config.json (" . e.Message . ") — login recovery may be limited")
}

GuardWriteResult(token) {
    global GUARD_RESULT
    try FileDelete(GUARD_RESULT)
    try FileAppend(token . " @ " . FormatTime(, "yyyy-MM-dd HH:mm:ss"), GUARD_RESULT, "UTF-8")
    LogMessage("  RESULT: " . token)
}

IsBravoHung(hwnd) {
    if !hwnd
        return false
    return DllCall("user32\IsHungAppWindow", "ptr", hwnd) ? true : false
}

LaunchBravo() {
    LogMessage("  launch: starting Bravo via .appref-ms shortcut")
    Run('cmd.exe /c start "" "' . BRAVO_APPREF . '"', , "Hide")
    deadline := A_TickCount + 120000
    while (A_TickCount < deadline) {
        if WinExist(BRAVO_WIN_TITLE)
            return true
        Sleep(1500)
    }
    return WinExist(BRAVO_WIN_TITLE) ? true : false
}

CloseAndRelaunch(force := false) {
    LogMessage("  relaunch: closing Bravo (force=" . (force ? "yes" : "no") . ")")
    hwnd := WinExist(BRAVO_WIN_TITLE)
    if (hwnd && !force) {
        ; graceful close — Bravo prompts to confirm exit
        try WinClose(BRAVO_WIN_TITLE)
        Sleep(2000)
        ; click any confirm button on the exit prompt
        for btn in ["close the program", "Yes", "OK", "Ok"] {
            try {
                if ClickByName(btn, 2500) {
                    LogMessage("    relaunch: clicked exit-confirm '" . btn . "'")
                    break
                }
            }
        }
        ; wait for the window to vanish
        gone := false
        deadline := A_TickCount + 25000
        while (A_TickCount < deadline) {
            if !WinExist(BRAVO_WIN_TITLE) {
                gone := true
                break
            }
            Sleep(1000)
        }
        if !gone
            force := true
    }
    if (force || WinExist(BRAVO_WIN_TITLE)) {
        LogMessage("    relaunch: force-killing Bravo.exe + dfsvc.exe")
        try Run('cmd.exe /c taskkill /F /IM Bravo.exe /T', , "Hide")
        Sleep(1500)
        try Run('cmd.exe /c taskkill /F /IM dfsvc.exe /T', , "Hide")
        Sleep(3000)
    }
    return LaunchBravo()
}

; --- recovery ladder --------------------------------------------------------
relaunchCount := 0
backToDashFails := 0
maxPasses := 8

Loop maxPasses {
    pass := A_Index
    LogMessage("  --- pass " . pass . "/" . maxPasses . " ---")

    hwnd := WinExist(BRAVO_WIN_TITLE)

    ; 0. no window
    if !hwnd {
        LogMessage("  state: no Bravo window")
        if (relaunchCount >= 3) {
            GuardWriteResult("FAIL_UNRECOVERABLE")
            ExitApp
        }
        relaunchCount++
        LaunchBravo()
        Sleep(3000)
        continue
    }

    ; 1. hung / Not Responding
    if IsBravoHung(hwnd) {
        LogMessage("  state: Bravo NOT RESPONDING (IsHungAppWindow)")
        if (relaunchCount >= 3) {
            GuardWriteResult("FAIL_UNRECOVERABLE")
            ExitApp
        }
        relaunchCount++
        CloseAndRelaunch(relaunchCount >= 2)   ; force on 2nd+ relaunch
        Sleep(3000)
        continue
    }

    ActivateBravo()
    Sleep(500)

    ; 2. dismiss ad popups + known modals (the ad has a "Close" button that
    ;    DismissPopups does not handle; do that here, then standard popups)
    dismissed := false
    for btn in ["Close", "Remind Me Later"] {
        try {
            if ClickByName(btn, 1500) {
                LogMessage("    dismissed popup button '" . btn . "'")
                dismissed := true
                Sleep(1200)
            }
        }
    }
    ; DevExpress / Bravo modal Ok+Cancel via AutomationId (defensive)
    for aid in ["PART_CancelDialogButton", "PART_OkDialogButton", "btnCancel"] {
        try {
            root := GetBravoRoot()
            el := root.FindElement({AutomationId: aid})
            if el {
                try el.InvokePattern.Invoke()
                LogMessage("    dismissed modal via " . aid)
                dismissed := true
                Sleep(1000)
            }
        }
    }
    try {
        if DismissPopups()
            dismissed := true
    }
    if dismissed {
        Sleep(800)
        continue   ; re-evaluate cleanly after dismissing
    }

    ; 3. login screen / session list
    if IsOnLoginScreen() {
        LogMessage("  state: login screen -> RecoverFromAutoLock")
        if (password = "") {
            GuardWriteResult("FAIL_UNRECOVERABLE")
            ExitApp
        }
        try RecoverFromAutoLock(password)
        Sleep(1500)
        continue
    }

    ; 4. on a Dashboard?  (title contains "VALLEY PAWN - ")
    if WaitForBravoReady(3) {
        GuardWriteResult("OK:" . GetCurrentStoreCode())
        ExitApp
    }

    ; 5. working view — store code present but not a Dashboard title
    code := GetCurrentStoreCode()
    if (code != "") {
        LogMessage("  state: working view (store " . code . ") -> BackToDashboard")
        if !BackToDashboard()
            backToDashFails++
        Sleep(1000)
        if (backToDashFails >= 2) {
            LogMessage("  BackToDashboard repeatedly failed -> escalate to relaunch")
            relaunchCount++
            backToDashFails := 0
            CloseAndRelaunch(relaunchCount >= 2)
            Sleep(3000)
        }
        continue
    }

    ; 6. limbo — responsive window, no store code, not login, not dashboard
    LogMessage("  state: LIMBO (no store code, responsive, not login/dashboard)")
    if !BackToDashboard()
        backToDashFails++
    Sleep(1000)
    if (backToDashFails >= 2) {
        if (relaunchCount >= 3) {
            GuardWriteResult("FAIL_UNRECOVERABLE")
            ExitApp
        }
        LogMessage("  limbo persists -> relaunch")
        relaunchCount++
        backToDashFails := 0
        CloseAndRelaunch(relaunchCount >= 2)
        Sleep(3000)
    }
}

; exhausted passes
if WaitForBravoReady(2)
    GuardWriteResult("OK:" . GetCurrentStoreCode())
else
    GuardWriteResult("FAIL_UNRECOVERABLE")
ExitApp
