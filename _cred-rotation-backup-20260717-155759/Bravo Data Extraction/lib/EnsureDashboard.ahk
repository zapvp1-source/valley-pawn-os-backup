; ============================================================================
; lib/EnsureDashboard.ahk - run-start Bravo readiness gate (root-cause fix)
;
; Why this file exists (2026-06-22):
;   Every Monday the combined run failed with "Bravo window not found/ready
;   within 30s" on ALL cells. Root cause: overnight Bravo cold-launches to the
;   "Select a store to work with" screen - BEFORE any login. Report handlers
;   require a logged-in store dashboard (title contains "VALLEY PAWN - <store>").
;   The existing recovery (RecoverFromAutoLock) only handles the login form and
;   the session list; NOTHING handled the store-select screen, so an unattended
;   run could never get past it and every cell timed out.
;
;   This gate is called ONCE at the start of ProcessTrigger (bravo_watcher.ahk)
;   BEFORE any cells run. It drives Bravo from whatever cold-start screen it is
;   on (store-select -> session list -> login form) to a logged-in dashboard,
;   then lets the normal per-cell EnsureStore/StoreCycle take over.
;
;   On failure it returns false and the watcher aborts the run cleanly (all
;   cells marked skipped/aborted). NO Slack post, NO DM - Joshua reviews runs
;   himself.
;
;   Additive: new file, new functions only. Existing handlers / lib untouched.
;   Depends on helpers already defined in lib/Bravo.ahk:
;     GetCurrentStoreCode, IsOnLoginScreen, ExistsByName, ClickByName,
;     DoubleClickByName, WaitForAnyByName, WaitForBravoReady, ActivateBravo,
;     DismissPopups, RecoverFromAutoLock, LogMessage, BRAVO_WIN_TITLE.
; ============================================================================
#Requires AutoHotkey v2.0

; How long to let a freshly-logged-in Bravo settle before running a report.
; A just-authenticated Bravo 2026.6.0.76 intermittently hangs on the heavy
; report export commit (produces a 0-byte file). Runs that succeed are on a
; Bravo that has been up a while. Settling after login - and only after login -
; gives the export commit far better odds. An already-up Bravo skips this.
global BRAVO_POST_LOGIN_SETTLE_MS := 90000   ; 90s

; True only on the cold-start "Select a store to work with" screen:
;   - not yet logged into a store (no store code in the title), AND
;   - not on the login form / session list (those expose Submit / Global Access
;     and are already handled by IsOnLoginScreen + RecoverFromAutoLock), AND
;   - the "Select" confirm button is present.
IsOnStoreSelectScreen() {
    if (GetCurrentStoreCode() != "")
        return false
    if IsOnLoginScreen()
        return false
    return ExistsByName("Select")
}

; Pick a store on the store-select screen and confirm. Returns true once Bravo
; has advanced to the session-list / login form (or straight to a dashboard).
HandleStoreSelectScreen(defaultStore := "CUL") {
    if !IsOnStoreSelectScreen()
        return true
    LogMessage("  StoreSelect: 'Select a store' screen detected -> choosing " . defaultStore)
    DismissPopups()  ; clear stray "Bravo is already running" / info dialogs

    ; Highlight the store row, then click Select. (Mirrors the manual recovery
    ; that is known to work.) Fall back to double-clicking the row in case this
    ; build advances on row activation rather than the Select button.
    clicked := false
    try {
        ClickByName(defaultStore, 5000)
        Sleep(400)
        ClickByName("Select", 5000)
        clicked := true
    } catch as e {
        LogMessage("  StoreSelect: row+Select click failed: " . e.Message)
    }
    if !clicked {
        try {
            DoubleClickByName(defaultStore, 5000)
            clicked := true
        } catch as e2 {
            LogMessage("  StoreSelect: double-click row failed: " . e2.Message)
            return false
        }
    }

    ; Wait for the next screen so RecoverFromAutoLock has something to act on.
    seen := WaitForAnyByName(["Resume Session", "New User", "Submit", "Global Access"], 20000)
    if (seen != "") {
        LogMessage("  StoreSelect: advanced to '" . seen . "' screen")
        return true
    }
    ; Fallback: straight to a REAL dashboard (no session-list / login markers).
    ; Note: a store code in the title is NOT sufficient - the session list also
    ; shows the store - so we must confirm the recovery markers are absent.
    if (IsTrueDashboard()) {
        LogMessage("  StoreSelect: advanced straight to a dashboard")
        return true
    }
    LogMessage("  StoreSelect: no login/session/dashboard screen appeared after Select")
    return false
}

; A real, logged-in store dashboard: store code in the title AND none of the
; login-form / session-list markers present. (Title alone is unreliable - the
; session list and login form both keep the store code in the title.)
IsTrueDashboard() {
    if (GetCurrentStoreCode() = "")
        return false
    if IsOnLoginScreen()                 ; Submit / Global Access -> login or session list
        return false
    if ExistsByName("Resume Session")    ; session list
        return false
    if ExistsByName("End Session")       ; session list
        return false
    return true
}

; Run-start readiness gate. Drives Bravo to a logged-in dashboard from any
; cold-start screen. Returns true if a dashboard is reached, false otherwise.
EnsureBravoDashboard(password, defaultStore := "CUL") {
    ; Bravo may be mid-relaunch (the foreground keeper restarts it after a
    ; crash, which lands on the cold store-select screen). Wait for the window
    ; to exist before inspecting screens.
    if !WinExist(BRAVO_WIN_TITLE) {
        LogMessage("  EnsureBravoDashboard: no Bravo window yet - waiting up to 120s for (re)launch")
        deadline := A_TickCount + 120000
        while (A_TickCount < deadline) {
            if WinExist(BRAVO_WIN_TITLE)
                break
            Sleep(2000)
        }
    }
    if !WinExist(BRAVO_WIN_TITLE) {
        LogMessage("  EnsureBravoDashboard: Bravo window never appeared")
        return false
    }
    ActivateBravo()
    DismissPopups()

    ; After a (re)launch the window can EXIST while Bravo is still loading -
    ; splash screen, ClickOnce check, or the store list still rendering. Wait
    ; for an ACTIONABLE screen (dashboard / store-select / login / session
    ; list) before the recovery loop, so we don't burn all our retries against
    ; a still-loading window. Up to 90s; the keeper handles any ClickOnce prompt.
    contentDeadline := A_TickCount + 90000
    loop {
        if (IsTrueDashboard() || IsOnStoreSelectScreen() || IsOnLoginScreen() || ExistsByName("Resume Session")) {
            break
        }
        if (A_TickCount > contentDeadline) {
            LogMessage("  EnsureBravoDashboard: no actionable screen within 90s (Bravo still loading?)")
            break
        }
        Sleep(3000)
        DismissPopups()
    }

    ; Fast path: already on a settled store dashboard - no settle needed.
    if IsTrueDashboard() {
        LogMessage("  EnsureBravoDashboard: already on dashboard (" . GetCurrentStoreCode() . ") - settled, no delay")
        return true
    }

    ; Cold-start store-select screen - the gap that broke every Monday.
    if IsOnStoreSelectScreen() {
        if !HandleStoreSelectScreen(defaultStore)
            return false
        DismissPopups()
    }

    ; Drive session-list / login form -> dashboard. Bravo can flash through
    ; transient frames right after store-select (the store code appears in the
    ; title before the session list / login form finish rendering), so a single
    ; recovery pass can race. Loop: if already on a true dashboard, done; else
    ; wait for a recoverable screen to settle, run the existing recovery helper,
    ; and re-check. Retry a few times before giving up.
    loop 6 {
        if IsTrueDashboard() {
            DismissPopups()
            ; We just logged in (the fast path missed, so a login happened).
            ; A freshly-logged-in Bravo 2026.6.0.76 intermittently hangs on the
            ; heavy report export commit (0-byte file); letting it settle first
            ; sharply reduces that. Settle only applies post-login - an already-
            ; up Bravo took the fast path above and skips this.
            LogMessage("  EnsureBravoDashboard: dashboard reached (" . GetCurrentStoreCode() . ") after login - settling " . (BRAVO_POST_LOGIN_SETTLE_MS // 1000) . "s before report")
            Sleep(BRAVO_POST_LOGIN_SETTLE_MS)
            DismissPopups()
            return true
        }
        DismissPopups()
        ; LOCKED / session screen: after store-switching the combined run leaves
        ; Bravo on a Lock-Session screen that shows "Resume Session" + "End
        ; Session" but NOT "Global Access" / "Submit". RecoverFromAutoLock's
        ; IsOnLoginScreen() guard treats that as "not a login screen" and
        ; no-ops, so we must click Resume Session ourselves to advance to the
        ; login form (or straight back to the dashboard). NEVER click End
        ; Session - that destroys the session and the saved username pre-fill.
        if (ExistsByName("Resume Session") && !IsOnLoginScreen()) {
            LogMessage("  EnsureBravoDashboard: locked/session screen -> Resume Session")
            try ClickByName("Resume Session", 4000)
            Sleep(2000)
            DismissPopups()
        }
        ; Now handle the login form / session list via the standard recovery.
        WaitForAnyByName(["Submit", "Global Access", "Resume Session", "New User"], 8000)
        RecoverFromAutoLock(password)
        Sleep(1500)
        DismissPopups()
    }
    if IsTrueDashboard() {
        LogMessage("  EnsureBravoDashboard: dashboard reached (" . GetCurrentStoreCode() . ") after login - settling " . (BRAVO_POST_LOGIN_SETTLE_MS // 1000) . "s before report")
        Sleep(BRAVO_POST_LOGIN_SETTLE_MS)
        DismissPopups()
        return true
    }
    LogMessage("  EnsureBravoDashboard: still not on a dashboard after recovery loop")
    return false
}
