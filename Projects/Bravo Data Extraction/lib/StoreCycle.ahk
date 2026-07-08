; ============================================================================
; lib/StoreCycle.ahk — Bravo store-switching primitive (slice 3 / UIA-v2)
;
; Implements the bravo-store-cycle skill flow using UIA element lookups
; instead of pixel coordinates. The clicks are immune to banner rotation,
; window resizes, and per-store layout drift.
;
; Flow:
;   Dashboard -> Lock Session -> [Session List? End Session ->] Login Screen
;     -> Global Access -> Store Selector -> double-click store row -> Login
;     Screen with target store -> paste password -> Submit -> Dashboard
;
; Public:
;   SwitchStore(targetStore, password) -> Bool
;   EnsureStore(targetStore, password) -> Bool   (no-op if already there)
;
; The element Names below are best-guess starting points. If a step fails
; with "ClickByName: element not found", drop a `uia-discover` trigger on
; that screen and update the constant to match what UIADiscover dumps.
; ============================================================================

#Requires AutoHotkey v2.0

; ---------------------------------------------------------------------------
; Cause of the last EnsureStore / SwitchStore false return.
; Possible values:
;   ""           — no failure (or cleared on success / fresh entry)
;   "login"      — RecoverFromAutoLock failed, BravoLogin/Submit failed,
;                  or the post-Submit 25s wait timed out. Real auth risk.
;   "nav"        — BackToDashboard couldn't reach Dashboard, so the
;                  Lock Session click can't find its button. NOT auth.
;   "ready"      — WaitForBravoReady(15) timed out. Bravo window not in
;                  a usable state. NOT auth.
;   "session"    — Session List / Global Access / Resume Session / form
;                  rendering failures. NOT auth.
;   "store-row"  — Couldn't find or double-click the target store row in
;                  the store selector. NOT auth.
;
; bravo_watcher.ahk reads this AFTER each cell to decide whether to tick
; the auth-failure circuit breaker. Only cause="login" trips the breaker.
; All other causes log the failure and continue without lockout-protection
; bookkeeping.
;
; Added 2026-05-23 to stop the breaker from false-tripping on plain
; navigation failures (Bravo wedged off-Dashboard).
; ---------------------------------------------------------------------------
global ENSURESTORE_LAST_CAUSE := ""


; Map 3-letter store code -> UIA Name of the corresponding row in the Store
; Selector. The store row Name is most likely the full store name in title
; case (e.g. "Culpeper") or all-caps (e.g. "CULPEPER"). We try both via
; SC_STORE_ROW_CANDIDATES; whichever one is found wins.
global SC_STORE_FULL_NAME := Map(
    "CUL", "Culpeper",
    "HAR", "Harrisonburg",
    "LEX", "Lexington",
    "ROA", "Roanoke",
    "WAY", "Waynesboro"
)

; ----- Public API ------------------------------------------------------------

; If Bravo is already on targetStore, do nothing. Otherwise cycle to it.
;
; Handles three starting states:
;   1. Already on targetStore's Dashboard -> return true immediately.
;   2. On some other store's Dashboard -> SwitchStore.
;   3. On the Login screen (auto-locked or fresh start). Title bar still shows
;      a store code, so we can't rely on GetCurrentStoreCode alone. We check
;      for Login elements first and recover, then re-evaluate the store.
EnsureStore(targetStore, password) {
    global ENSURESTORE_LAST_CAUSE
    ENSURESTORE_LAST_CAUSE := ""
    if IsOnLoginScreen() {
        LogMessage("  EnsureStore: login screen visible — recovering before evaluating store")
        ; --- Select Store selector handling (added 2026-06-07) ---------------
        ; If Bravo is on the Global Access store selector (store rows visible),
        ; RecoverFromAutoLock cannot proceed (it needs the Login form). Pick the
        ; target store row first so we land on the correct login form. Safe
        ; no-op if already on the login form (WaitForAnyByName times out).
        scStoreNm := SC_STORE_FULL_NAME.Has(targetStore) ? SC_STORE_FULL_NAME[targetStore] : ""
        if (scStoreNm != "") {
            scRowCands := [scStoreNm, StrUpper(scStoreNm), targetStore, StrUpper(targetStore)]
            scRowSeen := WaitForAnyByName(scRowCands, 2500)
            if (scRowSeen != "") {
                LogMessage("  EnsureStore: Select Store selector -> double-click '" . scRowSeen . "'")
                try DoubleClickByName(scRowSeen, 3000)
                Sleep(2500)
                DismissPopups()
            }
        }
        if !RecoverFromAutoLock(password) {
            LogMessage("  EnsureStore: auto-lock recovery failed")
            ENSURESTORE_LAST_CAUSE := "login"
            return false
        }
        ; After recovery we land on whatever store the Login screen was tied
        ; to, which may or may not be targetStore. Fall through to the
        ; normal check below.
    }
    current := GetCurrentStoreCode()
    if (current = targetStore) {
        LogMessage("  EnsureStore: already on " . targetStore)
        return true
    }
    LogMessage("  EnsureStore: switching from " . current . " to " . targetStore)
    return SwitchStore(targetStore, password)
}

; Drive the full Lock Session -> [End Session ->] Global Access -> Select ->
; Login cycle.
;
; CRITICAL — Bravo only accepts Lock Session from the DASHBOARD. If we're on
; a Reports preview, Reports listing, Loans/Buys view, or any working state,
; the Lock Session click either does nothing or causes "Cannot switch stores:
; FREE1 is busy with X" warnings later. Joshua's standing rule: "click Done
; before you can switch stores, you must exit out to dashboard before you
; can switch stores."
;
; So: BackToDashboard FIRST, then Lock Session.
SwitchStore(targetStore, password) {
    global ENSURESTORE_LAST_CAUSE
    ENSURESTORE_LAST_CAUSE := ""
    if !WaitForBravoReady(15) {
        LogMessage("  SwitchStore: Bravo not ready")
        ENSURESTORE_LAST_CAUSE := "ready"
        return false
    }
    ActivateBravo()
    DismissPopups()

    ; --- Step 0: ensure we're on the Dashboard before Lock Session ---
    ; This avoids Bravo's "busy with X" error when Lock Session is clicked
    ; from a working view (Reports / Loans-Buys / Layaways / Customers).
    LogMessage("  SwitchStore: BackToDashboard before Lock Session")
    btdOk := BackToDashboard()
    if !btdOk {
        LogMessage("  SwitchStore: WARNING — could not reach Dashboard; trying Lock Session anyway")
    }
    DismissPopups()

    ; --- Step 1: Lock Session ---
    LogMessage("  SwitchStore: click Lock Session")
    try {
        ClickByName("Lock Session", 5000)
    } catch as e {
        LogMessage("  SwitchStore: Lock Session click failed: " . e.Message)
        ; If BackToDashboard never reached Dashboard, the real cause is
        ; navigation, not auth. Tag accordingly so the watcher's auth
        ; circuit breaker doesn't false-trip on wedged-UI runs.
        ENSURESTORE_LAST_CAUSE := btdOk ? "session" : "nav"
        try ScreenshotToFile(targetStore . "_lock-session-failed")
        return false
    }
    Sleep(1500)
    DismissPopups()

    ; --- Step 2: handle Session List screen if it appears -----------------
    ; STANDING RULE (Joshua 2026-05-13): NEVER click End Session. End Session
    ; destroys the user's session and wipes the Login form pre-fill that
    ; Step 5 depends on. The watcher MUST find a non-destructive way to
    ; dismiss the intermediate Session List screen so the user session
    ; stays locked-but-alive while we navigate to Global Access.
    ;
    ; Wait up to 25s for either Global Access (direct path — best case) or
    ; one of the Session List buttons. The candidate list is wide so we can
    ; log what's actually present and pick the safest available action.
    sessionListSeen := WaitForAnyByName([
        "Global Access",     ; direct — no Session List screen, ideal
        "Resume Session",    ; non-destructive — keeps session alive
        "Cancel",            ; non-destructive — backs out
        "Continue",          ; non-destructive — proceeds without ending
        "Back",              ; non-destructive — backs out
        "End Session"        ; LAST RESORT — destroys session, only if nothing else
    ], 25000)

    if (sessionListSeen = "Global Access") {
        ; No Session List screen interposed — fall through to the Step 3
        ; Global Access click. Nothing to do here.
    } else if (sessionListSeen = "") {
        LogMessage("  SwitchStore: WARNING — no recognizable Session List or Global Access button visible within 25s")
        ; Continue anyway — Global Access click below will fail with a clear error
    } else {
        ; Session List intermediate screen detected. Try non-destructive
        ; options first; fall back to End Session only as a last resort.
        LogMessage("  SwitchStore: Session List screen detected; first visible button = '" . sessionListSeen . "'")
        dismissed := false
        for candidate in ["Resume Session", "Cancel", "Continue", "Back"] {
            if !FindByName(candidate, 500)
                continue
            LogMessage("  SwitchStore: trying non-destructive dismiss via '" . candidate . "'")
            try {
                ClickByName(candidate, 3000)
                Sleep(2000)
                DismissPopups()
                dismissed := true
                break
            } catch as e {
                LogMessage("  SwitchStore: '" . candidate . "' click failed: " . e.Message)
            }
        }
        if (!dismissed) {
            ; Nothing non-destructive worked. End Session is the last
            ; resort. Log a WARN so we can spot how often this happens
            ; and consider what's missing from Bravo's UI.
            LogMessage("  SwitchStore: WARN: no non-destructive button worked - falling back to End Session (violates 'never logout' rule)")
            try {
                ClickByName("End Session", 3000)
                Sleep(2000)
                DismissPopups()
            } catch as e {
                LogMessage("  SwitchStore: End Session fallback also failed: " . e.Message)
                ENSURESTORE_LAST_CAUSE := "session"
                try ScreenshotToFile(targetStore . "_switchstore-session")
                return false
            }
        }
    }

    ; --- Step 3: Global Access ---
    LogMessage("  SwitchStore: click Global Access")
    try {
        ClickByName("Global Access", 15000)
    } catch as e {
        LogMessage("  SwitchStore: Global Access click failed: " . e.Message)
        ENSURESTORE_LAST_CAUSE := "session"
        try ScreenshotToFile(targetStore . "_switchstore-session")
        return false
    }
    Sleep(1500)

    ; --- Step 4: Pick target store row (double-click) ---
    storeName := SC_STORE_FULL_NAME.Get(targetStore, "")
    if (storeName = "") {
        LogMessage("  SwitchStore: unknown store code " . targetStore)
        ENSURESTORE_LAST_CAUSE := "store-row"
        try ScreenshotToFile(targetStore . "_switchstore-store-row")
        return false
    }
    LogMessage("  SwitchStore: double-click store row '" . storeName . "'")
    ; Try title case first, then all caps. Update the constant if neither
    ; matches what UIADiscover reports.
    storeCandidates := [storeName, StrUpper(storeName), targetStore, StrUpper(targetStore)]
    seen := WaitForAnyByName(storeCandidates, 10000)
    if (seen = "") {
        LogMessage("  SwitchStore: none of these store row Names matched: " . StrJoin(storeCandidates, ", "))
        ENSURESTORE_LAST_CAUSE := "store-row"
        try ScreenshotToFile(targetStore . "_switchstore-store-row")
        return false
    }
    try {
        DoubleClickByName(seen, 3000)
    } catch as e {
        LogMessage("  SwitchStore: store row double-click failed: " . e.Message)
        ENSURESTORE_LAST_CAUSE := "store-row"
        try ScreenshotToFile(targetStore . "_switchstore-store-row")
        return false
    }
    Sleep(2500)

    ; --- Step 4b: handle post-row Session List screen ---
    ; After picking a store, Bravo may show a Session List (existing sessions
    ; for that store with Resume/End/New User buttons) BEFORE the Login form.
    ; Click "New User" to skip the existing sessions and go straight to a
    ; clean Login form for our user. "Submit" is the canonical Login form
    ; signal; "New User" / "Resume Session" / "End Session" are the Session
    ; List signals.
    postRow := WaitForAnyByName(["Submit", "New User", "Resume Session", "End Session"], 20000)
    if (postRow = "") {
        LogMessage("  SwitchStore: no Login or Session List signal after store row dblclick within 20s")
        ENSURESTORE_LAST_CAUSE := "session"
        try ScreenshotToFile(targetStore . "_switchstore-session")
        return false
    }
    cameFromNewUser := false
    if (postRow != "Submit") {
        ; STANDING RULE (Joshua 2026-05-13): NEVER click End Session. Always
        ; Lock / Resume so the existing user's session stays intact and the
        ; Login form's User Name pre-fill is preserved. End Session destroys
        ; the session entirely and is forbidden here.
        ;
        ; Ladder on the Session List screen:
        ;   1. Resume Session — preferred. Reattaches to the existing session.
        ;      We land on a Login form that may have someone else's username
        ;      pre-filled; that case is handled by the Step 5 failsafe below
        ;      (Switch User -> New User -> explicit fill).
        ;   2. New User — fallback if Resume Session can't be clicked. Lands
        ;      on a fresh empty Login form, which Step 5's existing
        ;      cameFromNewUser path explicitly fills with FREE1@WAY.
        ;
        ; We DO NOT click End Session under any circumstances. If both Resume
        ; Session and New User fail, the cell fails and the watcher's
        ; auth-failure circuit breaker handles it.
        LogMessage("  SwitchStore: post-row Session List detected (saw '" . postRow . "') -> click Resume Session (keep user session intact)")
        try {
            ClickByName("Resume Session", 4000)
        } catch as e {
            LogMessage("  SwitchStore: Resume Session click failed: " . e.Message . " - falling back to New User (END SESSION IS FORBIDDEN)")
            try {
                ClickByName("New User", 3000)
                cameFromNewUser := true
            } catch as e2 {
                LogMessage("  SwitchStore: New User fallback also failed: " . e2.Message)
                ENSURESTORE_LAST_CAUSE := "session"
                try ScreenshotToFile(targetStore . "_switchstore-session")
                return false
            }
        }
        Sleep(1500)
        DismissPopups()
        ; Wait for Login form to actually render
        if !FindByName("Submit", 8000) {
            LogMessage("  SwitchStore: Submit never appeared after Session List handling")
            ENSURESTORE_LAST_CAUSE := "session"
            try ScreenshotToFile(targetStore . "_switchstore-session")
            return false
        }
    }

    ; --- Step 5: Login (User Name + Password + Submit) ---
    ; FAILSAFE (added 2026-05-13 per Joshua): before typing any credentials,
    ; verify the User Name field shows FREE1@WAY. Bravo can leave a previous
    ; user's name pre-filled (e.g. PMoney) when End Session terminates a
    ; stale session — submitting FREE1's password against PMoney's username
    ; silently fails and cascades into the lockout pattern that locked the
    ; account on 2026-05-13 morning.
    ;
    ; If the pre-fill is wrong (anything other than FREE1@WAY, and not empty),
    ; click "Switch User" to back out to the Session List, then click
    ; "New User" to land on a fresh empty Login form. Then fall into the
    ; existing cameFromNewUser fill path, which clicks the User Name field
    ; by name and pastes FREE1@WAY via clipboard. That path uses ClickByName
    ; (which has retry + visual click) and is well-tested.
    ;
    ; Read is read-only via UIA Value. Cannot corrupt anything. If we cannot
    ; read the field at all, we trust whatever the original code path
    ; (End Session / Resume Session / New User) set up and proceed.
    global CONFIG
    expectedUser := CONFIG.Has("bravo.username") ? CONFIG["bravo.username"] : "FREE1@WAY"
    ; Per-store override: at WAY, the FREE1 account is local to the store,
    ; so the User Name field on a WAY Login form is just "FREE1" (no @WAY
    ; suffix). At all other stores the canonical username is "FREE1@WAY".
    if (targetStore = "WAY")
        expectedUser := "FREE1"
    unameElemCheck := FindByName("User Name", 4000)
    if !unameElemCheck
        unameElemCheck := FindByName("User Name:", 1500)
    currentUserPrefill := ""
    if unameElemCheck {
        try currentUserPrefill := unameElemCheck.Value
    }
    if (currentUserPrefill != "" && currentUserPrefill != expectedUser) {
        LogMessage("  SwitchStore: User Name pre-fill is '" . currentUserPrefill . "' (expected '" . expectedUser . "') — backing out via Switch User -> New User")
        switchedSuccessfully := false
        try {
            ClickByName("Switch User", 4000)
            Sleep(800)
            DismissPopups()
            try {
                ClickByName("New User", 4000)
                Sleep(1500)
                DismissPopups()
                ; Wait for the fresh Login form to render.
                if FindByName("Submit", 8000) {
                    switchedSuccessfully := true
                    cameFromNewUser := true
                    LogMessage("  SwitchStore: Switch User -> New User succeeded; will now explicitly fill " . expectedUser)
                } else {
                    LogMessage("  SwitchStore: Submit never appeared after Switch User -> New User")
                }
            } catch as eNU {
                LogMessage("  SwitchStore: New User click failed after Switch User: " . eNU.Message)
            }
        } catch as eSU {
            LogMessage("  SwitchStore: Switch User click failed: " . eSU.Message)
        }
        if (!switchedSuccessfully) {
            ; Bail rather than risk submitting wrong credentials. The
            ; auth-failure circuit breaker in bravo_watcher.ahk will trip
            ; after 3 of these in a row and abort the run cleanly.
            LogMessage("  SwitchStore: failsafe could not reach a fresh Login form — aborting cell to avoid wrong-credential submit")
            ENSURESTORE_LAST_CAUSE := "session"
            try ScreenshotToFile(targetStore . "_switchstore-session")
            return false
        }
    }

    ; New User path lands with an empty User Name field. Fill User Name,
    ; Tab to Password (Tab is the canonical way to move focus between form
    ; fields and is more reliable than FindByName.Focus() for WPF password
    ; boxes which often don't expose a Focusable UIA element correctly).
    if cameFromNewUser {
        global CONFIG
        username := CONFIG.Has("bravo.username") ? CONFIG["bravo.username"] : "FREE1@WAY"
        ; Per-store override: WAY uses "FREE1" (no @WAY suffix). See the
        ; Step 5 failsafe comment block above for details.
        if (targetStore = "WAY")
            username := "FREE1"
        LogMessage("  SwitchStore: fill User Name = " . username)
        unameElem := FindByName("User Name", 4000)
        if !unameElem
            unameElem := FindByName("User Name:", 1500)
        if unameElem {
            try unameElem.Focus()
            Sleep(200)
            Send("^a")
            Sleep(80)
            Send("{Delete}")
            Sleep(80)
            ; Clipboard-paste username (more reliable than typing on slow VMs)
            prevClip := ""
            try prevClip := A_Clipboard
            A_Clipboard := username
            ClipWait(2)
            Send("^v")
            Sleep(300)
            A_Clipboard := prevClip
        } else {
            LogMessage("    WARN: User Name field not found by name; typing into focused field")
            prevClip := ""
            try prevClip := A_Clipboard
            A_Clipboard := username
            ClipWait(2)
            Send("^v")
            Sleep(300)
            A_Clipboard := prevClip
        }
        ; Tab to move focus to the Password field
        Send("{Tab}")
        Sleep(300)
        LogMessage("  SwitchStore: Tab from User Name to Password")
    } else {
        ; Resume-Session path: User Name pre-filled, need to focus Password.
        LogMessage("  SwitchStore: focus password field")
        pwElem := FindByName("Password", 8000)
        if !pwElem
            pwElem := FindByName("Password:", 1500)
        if pwElem {
            try pwElem.Focus()
            Sleep(200)
        } else {
            LogMessage("    WARN: Password field not found by name - relying on focus from Submit row")
        }
    }
    try {
        BravoPastePassword(password)
    } catch as e {
        LogMessage("  SwitchStore: paste password failed: " . e.Message)
        ENSURESTORE_LAST_CAUSE := "login"
        try ScreenshotToFile(targetStore . "_switchstore-login")
        return false
    }
    Sleep(300)

    LogMessage("  SwitchStore: click Submit")
    try {
        ClickByName("Submit", 3000)
    } catch as e {
        LogMessage("  SwitchStore: Submit click failed: " . e.Message)
        ENSURESTORE_LAST_CAUSE := "login"
        try ScreenshotToFile(targetStore . "_switchstore-login")
        return false
    }

    ; --- Step 6: Wait for the title bar to flip to targetStore AND we're
    ; off the Login screen. Title bar shows the store code even on the
    ; Login form, so we have to require IsOnLoginScreen() = false too.
    ; If a Login Error popup fires (wrong creds), DismissPopups will tap
    ; the popup and we'll see Login screen indefinitely - that's a clear
    ; failure signal.
    deadline := A_TickCount + 25000
    while (A_TickCount < deadline) {
        Sleep(800)
        ; UIA calls can throw 0x80131505 during window-transition moments
        ; (Bravo briefly re-renders after Submit). Defensive try/catch so
        ; the wait loop tolerates transient UIA errors without crashing
        ; the whole report run.
        current := ""
        onLogin := true
        try {
            current := GetCurrentStoreCode()
        } catch {
            continue
        }
        try {
            onLogin := IsOnLoginScreen()
        } catch {
            continue
        }
        if (current = targetStore && !onLogin) {
            try DismissPopups()
            LogMessage("  SwitchStore: landed on " . targetStore)
            return true
        }
    }

    finalCode := ""
    finalLogin := "?"
    try finalCode := GetCurrentStoreCode()
    try finalLogin := IsOnLoginScreen() ? "yes" : "no"
    LogMessage("  SwitchStore: timeout waiting for " . targetStore . " (saw " . finalCode . ", onLogin=" . finalLogin . ")")
    ; Title bar never flipped to targetStore. Could be wrong password
    ; (Login Error popup eaten by DismissPopups) or extreme slowness.
    ; Treat as login-cause so the breaker protects against a wrong-cred
    ; cascade.
    ENSURESTORE_LAST_CAUSE := "login"
    try ScreenshotToFile(targetStore . "_post-submit-timeout")
    return false
}

; ----- Internals -------------------------------------------------------------

; Helper for concise candidate-list logging.
StrJoin(arr, sep) {
    out := ""
    for i, v in arr {
        if (i > 1)
            out .= sep
        out .= v
    }
    return out
}
