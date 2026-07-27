; ============================================================================
; lib/Bravo.ahk — Bravo POS app wrapper
;
; Common helpers used by every report module:
;   - ActivateBravo, WaitForBravoReady
;   - GetCurrentStoreCode (reads title bar — source of truth)
;   - BravoLogin (paste password via clipboard)
;   - DismissPopups (handles "Overdue Task Reminder" etc)
;   - BackToDashboard
;   - LogMessage (timestamped log writer)
;   - ToCsvField (safe CSV field quoting)
;   - WriteCsvRow (append a row to a CSV file)
;
; Conventions:
;   - Title bar of an authenticated Bravo window: "Bravo  2026.2.2.3  VALLEY PAWN - <STORE> (<CODE>)"
;   - Bravo can be slow — every Click/Send is paired with a sensible Sleep.
;   - Never type the password with Send(). Use clipboard + Ctrl+V.
; ============================================================================

#Requires AutoHotkey v2.0
#Include UIA-v2\UIA.ahk

; CRITICAL: all our click coordinates were captured from full-screen screenshots,
; so we drive the mouse in SCREEN coordinates. AHK v2's default for Click is
; "Client" (relative to the active window's client area) which would offset every
; click by the title bar height.
;
; NOTE (slice 3): Most click sites are migrating to UIA element lookups (see
; UIA helpers below) which don't depend on coordinates at all. CoordMode still
; matters for any remaining coordinate-based fallback or DismissPopups Enter
; presses.
CoordMode "Mouse", "Screen"
CoordMode "Pixel", "Screen"

; ----- Window identification -------------------------------------------------

; Bravo's main window class — set during runtime. We discover it on first
; activation rather than hard-coding, in case the WPF window class shifts
; between Bravo versions.
global BRAVO_WIN_TITLE := "Bravo "       ; matches any window whose title starts with "Bravo "
global BRAVO_LOG_PATH := ""              ; set by InitLog() per run

; ----- Activation ------------------------------------------------------------

; Bring Bravo to the front. Returns true if found and activated.
ActivateBravo() {
    if WinExist(BRAVO_WIN_TITLE) {
        WinActivate(BRAVO_WIN_TITLE)
        WinWaitActive(BRAVO_WIN_TITLE, , 5)
        Sleep(300)
        return true
    }
    return false
}

; Block until Bravo's window exists and looks ready (title contains "VALLEY PAWN - ").
; Returns true if ready within timeoutSec, false otherwise.
WaitForBravoReady(timeoutSec := 30) {
    deadline := A_TickCount + timeoutSec * 1000
    loop {
        if WinExist(BRAVO_WIN_TITLE) {
            title := WinGetTitle(BRAVO_WIN_TITLE)
            if InStr(title, "VALLEY PAWN - ") {
                return true
            }
        }
        if (A_TickCount > deadline)
            return false
        Sleep(500)
    }
}

; ----- UIA helpers (slice 3) -------------------------------------------------
;
; UIA-v2 wraps Microsoft's UI Automation framework: every WPF element has a
; Name, an AutomationId, and a ControlType, and we can look up elements by
; those attributes instead of clicking pixel coordinates. This is immune to
; window resizes, DPI changes, banner rotation, and per-store layout drift —
; the failure modes that broke slice 1/2.
;
; Conventions:
;   - All helpers take a `name` (matched against the UIA Name property).
;   - timeoutMs > 0 polls until the element appears (or returns 0 on timeout).
;   - timeoutMs = 0 is a single-shot lookup, returns 0 immediately if missing.
;   - All helpers log via LogMessage so failures land in the per-trigger log.
;   - Errors throw; report modules should wrap calls in try/catch when they
;     want to handle missing elements gracefully (e.g. Session List detection).
;
; UIA-v2 library auto-initializes on first UIA.* reference; no explicit init.

; Resolve the root UIA element for the Bravo window. Throws if not found.
GetBravoRoot() {
    hwnd := WinExist(BRAVO_WIN_TITLE)
    if !hwnd
        throw Error("GetBravoRoot: Bravo window not found")
    ; UIA.ElementFromHandle intermittently throws 0x80131505 ("cannot get Bravo
    ; root") when the UIA provider is momentarily busy/rebuilding during heavy
    ; screen transitions. It succeeds on a quick retry. Retry up to 6x so a
    ; transient hiccup does not fail the whole cell. Additive: success path
    ; unchanged. (2026-06-30)
    lastErr := ""
    Loop 6 {
        try {
            return UIA.ElementFromHandle(hwnd)
        } catch as e {
            lastErr := e
            Sleep(500)
            hwnd := WinExist(BRAVO_WIN_TITLE)
            if !hwnd
                throw Error("GetBravoRoot: Bravo window not found")
        }
    }
    if lastErr
        throw lastErr
    throw Error("GetBravoRoot: UIA.ElementFromHandle failed after retries")
}

; Find an element by Name. Returns the element, or 0 if not found.
; timeoutMs > 0 polls until the element appears.
FindByName(name, timeoutMs := 0, parent := "") {
    root := 0
    if parent {
        root := parent
    } else {
        try {
            root := GetBravoRoot()
        } catch {
            return 0
        }
    }
    if !root
        return 0
    if (timeoutMs <= 0) {
        try {
            return root.FindElement({Name: name})
        } catch {
            return 0
        }
    }
    deadline := A_TickCount + timeoutMs
    loop {
        try {
            elem := root.FindElement({Name: name})
            if elem
                return elem
        } catch {
            ; element not present yet, or transient UIA error - keep polling
        }
        if (A_TickCount > deadline)
            return 0
        Sleep(200)
        ; Re-acquire root in case the window changed mid-poll
        if !parent {
            try root := GetBravoRoot()
            catch {
                root := 0
            }
            if !root
                continue
        }
    }
}

; Click an element by Name. Throws if not found within timeoutMs.
; Returns the clicked element so callers can chain follow-up checks.
; IMPORTANT: pass "left" so UIA-v2 does a PHYSICAL mouse click rather than
; falling back to InvokePattern. WPF tree-view items (like Bravo's right-
; sidebar Reports button) require a physical click to fire navigation —
; pattern-based clicks only select.
ClickByName(name, timeoutMs := 5000, parent := "") {
    elem := FindByName(name, timeoutMs, parent)
    if !elem
        throw Error("ClickByName: element not found: " . name)
    elem.Click("left")
    LogMessage("    [UIA] click " . name)
    return elem
}

; Double-click an element by Name. Used for Store Selector rows in Bravo.
DoubleClickByName(name, timeoutMs := 5000, parent := "") {
    elem := FindByName(name, timeoutMs, parent)
    if !elem
        throw Error("DoubleClickByName: element not found: " . name)
    elem.Click("Left", 2)
    LogMessage("    [UIA] dblclick " . name)
    return elem
}

; Existence check. Returns true/false.
ExistsByName(name, parent := "") {
    return !!FindByName(name, 0, parent)
}

; Wait for any of several named elements to appear. Returns the name of the
; first one seen, or "" on timeout. Used to disambiguate between screens
; (e.g. "Resume Session" -> Session List, "Username" -> Login).
WaitForAnyByName(names, timeoutMs := 10000) {
    deadline := A_TickCount + timeoutMs
    loop {
        for n in names {
            if ExistsByName(n)
                return n
        }
        if (A_TickCount > deadline)
            return ""
        Sleep(200)
    }
}

; Set the value of an editable element by Name. Tries ValuePattern first,
; falls back to focus + clipboard paste for elements that don't expose Value.
SetValueByName(name, value, timeoutMs := 5000) {
    elem := FindByName(name, timeoutMs)
    if !elem
        throw Error("SetValueByName: element not found: " . name)
    try {
        elem.Value := value
        LogMessage("    [UIA] set " . name . " = " . value)
        return
    } catch {
        ; ValuePattern not supported — fall back to focus + clipboard paste
    }
    try elem.Focus()
    Sleep(100)
    Send("^a")
    Sleep(50)
    Send("{Delete}")
    Sleep(50)
    prev := ""
    try prev := A_Clipboard
    A_Clipboard := value
    if !ClipWait(2)
        throw Error("SetValueByName: clipboard did not receive value")
    Send("^v")
    Sleep(200)
    A_Clipboard := prev
    LogMessage("    [UIA] paste " . name . " = " . value)
}

; Toggle a checkbox/toggle element to the desired state. Returns true if a
; state change was needed and performed, false if already in target state.
SetToggleByName(name, desiredOn, timeoutMs := 5000) {
    elem := FindByName(name, timeoutMs)
    if !elem
        throw Error("SetToggleByName: element not found: " . name)
    try {
        current := elem.ToggleState  ; 0 = off, 1 = on, 2 = indeterminate
    } catch {
        ; Fall back to clicking once if we can't read state
        elem.Click()
        LogMessage("    [UIA] toggle " . name . " (state unreadable — single click)")
        return true
    }
    if (desiredOn && current = 1) || (!desiredOn && current = 0) {
        LogMessage("    [UIA] toggle " . name . " already " . (desiredOn ? "on" : "off"))
        return false
    }
    elem.Click()
    LogMessage("    [UIA] toggle " . name . " -> " . (desiredOn ? "on" : "off"))
    return true
}

; Read the value of an element by Name. Returns "" if not found or unreadable.
GetValueByName(name, timeoutMs := 0) {
    elem := FindByName(name, timeoutMs)
    if !elem
        return ""
    try return elem.Value
    try return elem.Name
    return ""
}

; Diagnostic: log every named clickable-looking element currently in the Bravo
; tree. Used in error paths so a failed run reveals what's actually on screen
; without needing a separate uia-discover trigger.
;
; Logs at most ~maxItems entries per category so even a busy screen stays
; readable. Output goes into the per-trigger log.
LogVisibleNames(maxItems := 40) {
    LogMessage("    [diag] enumerating visible named elements:")
    try {
        root := GetBravoRoot()
    } catch as e {
        LogMessage("    [diag] cannot get Bravo root: " . e.Message)
        return
    }
    ; Walk by control type. UIA enum order isn't guaranteed, but FindElements
    ; returns descendants in document order, which is usually close to visual.
    for typeName in ["Button", "Hyperlink", "TreeViewItem", "Text", "Edit", "CheckBox", "ComboBox", "MenuItem"] {
        DumpByType(root, typeName, maxItems)
    }
}

; Internal — list at most maxItems named elements of one type.
DumpByType(root, typeName, maxItems) {
    count := 0
    try {
        elems := root.FindElements({Type: typeName})
    } catch {
        return
    }
    if (!elems || elems.Length = 0)
        return
    for elem in elems {
        try {
            n := elem.Name
        } catch {
            continue
        }
        if (n = "")
            continue
        ; Truncate very long names so the log stays readable
        display := (StrLen(n) > 80) ? SubStr(n, 1, 77) . "..." : n
        autoId := ""
        try autoId := elem.AutomationId
        if (autoId != "")
            LogMessage("    [diag] " . typeName . ": '" . display . "' (AutoId=" . autoId . ")")
        else
            LogMessage("    [diag] " . typeName . ": '" . display . "'")
        if (++count >= maxItems) {
            LogMessage("    [diag]   ... (" . typeName . " truncated at " . maxItems . ")")
            return
        }
    }
}

; ----- Login screen detection & auto-lock recovery (slice 3 / step 9) -------
;
; Bravo auto-locks after some idle period; mid-flow operations need to detect
; that and re-login. Also covers the case where Bravo is left on the Login
; screen between sessions (Joshua's recovery state on 2026-05-12).
;
; Heuristic for "we're on the Login screen":
;   - Title bar still shows a store code (Bravo doesn't drop it on lock)
;   - But the "Submit" button OR "Global Access" link is visible
; Either of those two named elements is sufficient — they don't appear in the
; authenticated UI. We check the cheaper / more diagnostic one first.

IsOnLoginScreen() {
    ; "Global Access" is distinctive — only on Login. "Submit" is the actual
    ; login form's submit button.
    return ExistsByName("Global Access") || ExistsByName("Submit")
}

; If we're sitting on the Login screen, paste the password and submit.
; Returns true if we successfully landed on a Dashboard (store code in title),
; false on timeout / failure. No-op + returns true if not on Login screen.
RecoverFromAutoLock(password) {
    if !IsOnLoginScreen() {
        return true
    }
    LogMessage("  RecoverFromAutoLock: login screen detected, submitting password")

    ; If we're on the Session List screen (not the actual Login form), first
    ; click Resume Session to get to the Login form. Session List shows
    ; New User / End Session / Resume Session; Login form shows Submit.
    if !ExistsByName("Submit") {
        if ExistsByName("Resume Session") {
            LogMessage("    RecoverFromAutoLock: Session List detected -> Resume Session")
            try ClickByName("Resume Session", 3000)
            Sleep(2000)
            DismissPopups()
        } else if ExistsByName("New User") {
            LogMessage("    RecoverFromAutoLock: Session List detected -> New User")
            try ClickByName("New User", 3000)
            Sleep(2000)
            DismissPopups()
        }
        if !FindByName("Submit", 8000) {
            LogMessage("    RecoverFromAutoLock: Submit never appeared after Session List handling")
            return false
        }
    }

    ; FAILSAFE (added 2026-05-13 per Joshua): verify User Name pre-fill is
    ; FREE1@WAY before submitting password. If wrong, back out via Switch
    ; User -> New User to a fresh Login form, then explicitly type
    ; FREE1@WAY via ClickByName + clipboard paste (same approach as the
    ; cameFromNewUser branch in StoreCycle.ahk). See recovery.md "Failsafe
    ; — login user is always FREE1@WAY" for the full rule.
    global CONFIG
    autoLockExpectedUser := "FREE1@WAY"
    try {
        if IsObject(CONFIG) && CONFIG.Has("bravo.username")
            autoLockExpectedUser := CONFIG["bravo.username"]
    }
    ; Per-store override: at WAY, the FREE1 account is local to the store so
    ; the username is just "FREE1" (no @WAY suffix). Read the current store
    ; from the title bar to decide which form to expect.
    try {
        autoLockCurrentStore := GetCurrentStoreCode()
        if (autoLockCurrentStore = "WAY")
            autoLockExpectedUser := "FREE1"
    }
    autoLockUnameElem := FindByName("User Name", 3000)
    if !autoLockUnameElem
        autoLockUnameElem := FindByName("User Name:", 1500)
    autoLockPrefill := ""
    if autoLockUnameElem {
        try autoLockPrefill := autoLockUnameElem.Value
    }
    if (autoLockPrefill != "" && autoLockPrefill != autoLockExpectedUser) {
        LogMessage("    RecoverFromAutoLock: User Name pre-fill is '" . autoLockPrefill . "' (expected '" . autoLockExpectedUser . "') — backing out via Switch User -> New User")
        autoLockFreshFormOk := false
        try {
            ClickByName("Switch User", 4000)
            Sleep(800)
            DismissPopups()
            try {
                ClickByName("New User", 4000)
                Sleep(1500)
                DismissPopups()
                if FindByName("Submit", 8000)
                    autoLockFreshFormOk := true
                else
                    LogMessage("    RecoverFromAutoLock: Submit never appeared after Switch User -> New User")
            } catch as eNU {
                LogMessage("    RecoverFromAutoLock: New User click failed: " . eNU.Message)
            }
        } catch as eSU {
            LogMessage("    RecoverFromAutoLock: Switch User click failed: " . eSU.Message)
        }
        if (autoLockFreshFormOk) {
            ; Form is fresh and empty — explicitly fill User Name with the
            ; service account. ClickByName on the field is the trustworthy
            ; way to set focus before keystrokes.
            LogMessage("    RecoverFromAutoLock: explicitly filling User Name = " . autoLockExpectedUser)
            try {
                ClickByName("User Name", 4000)
                Sleep(200)
                Send("^a")
                Sleep(80)
                Send("{Delete}")
                Sleep(80)
                prevClipAL := ""
                try prevClipAL := A_Clipboard
                A_Clipboard := autoLockExpectedUser
                ClipWait(2)
                Send("^v")
                Sleep(300)
                A_Clipboard := prevClipAL
                Send("{Tab}")
                Sleep(200)
            } catch as eFill {
                LogMessage("    RecoverFromAutoLock: User Name fill failed: " . eFill.Message . " — aborting recovery")
                return false
            }
        } else {
            ; Could not reach a fresh form. Bail rather than submit wrong
            ; credentials. The watcher's circuit breaker will see this as
            ; an EnsureStore failure and trip after 3 in a row.
            LogMessage("    RecoverFromAutoLock: failsafe could not reach a fresh Login form — aborting recovery to avoid wrong-credential submit")
            return false
        }
    }

    ; Find the password field. Common UIA Names on WPF password boxes:
    ;   "Password", "Password:", or the AutomationId "PasswordBox".
    pwElem := FindByName("Password", 3000)
    if !pwElem
        pwElem := FindByName("Password:", 1500)
    if pwElem {
        try pwElem.Focus()
        Sleep(200)
    }
    BravoPastePassword(password)
    Sleep(300)
    try {
        ClickByName("Submit", 5000)
    } catch as e {
        LogMessage("    RecoverFromAutoLock: could not click Submit: " . e.Message)
        return false
    }
    ; Wait for Dashboard — store code in title bar AND Login elements gone.
    deadline := A_TickCount + 20000
    while (A_TickCount < deadline) {
        Sleep(500)
        if (GetCurrentStoreCode() != "" && !IsOnLoginScreen()) {
            DismissPopups()
            LogMessage("  RecoverFromAutoLock: landed on " . GetCurrentStoreCode())
            return true
        }
    }
    LogMessage("  RecoverFromAutoLock: timeout waiting for Dashboard")
    return false
}

; ----- Store identification --------------------------------------------------

; Read the Bravo title bar and extract the store code (CUL/HAR/LEX/ROA/WAY).
; Returns "" if no Bravo window or title doesn't match.
GetCurrentStoreCode() {
    if !WinExist(BRAVO_WIN_TITLE)
        return ""
    title := WinGetTitle(BRAVO_WIN_TITLE)
    ; Match "(CUL)" / "(HAR)" / "(LEX)" / "(ROA)" / "(WAY)" near end of title
    if RegExMatch(title, "\(([A-Z]{3})\)\s*$", &m)
        return m[1]
    return ""
}

; Like GetCurrentStoreCode but the full store name, e.g. "CULPEPER".
GetCurrentStoreName() {
    if !WinExist(BRAVO_WIN_TITLE)
        return ""
    title := WinGetTitle(BRAVO_WIN_TITLE)
    if RegExMatch(title, "VALLEY PAWN - ([A-Z]+)\s*\([A-Z]{3}\)", &m)
        return m[1]
    return ""
}

; ----- Login -----------------------------------------------------------------

; Type the password into Bravo's password field via clipboard + Ctrl+V.
; ASSUMPTION: cursor is already focused in the password field.
; The skill file (bravo-store-cycle) is explicit that Send() can drop keystrokes
; on slow VMs — always use clipboard.
BravoPastePassword(password) {
    prevClip := ""
    try prevClip := A_Clipboard
    A_Clipboard := password
    if !ClipWait(2)
        throw Error("Clipboard never received password")
    Send("^v")
    Sleep(300)
    A_Clipboard := prevClip  ; restore
}

; ----- Popups ----------------------------------------------------------------

; Dismiss known transient dialogs that appear after login or during navigation.
; Currently handles:
;   - "Overdue Task Reminder" (Remind Me Later button)
;   - "Information" popup with text "Till must be opened to complete a transaction"
;     (fires repeatedly on HAR when no till is open — Ok dismisses it)
; Add new pop-up patterns here as we discover them.
;
; Call this both at startup and after any nav step that might trigger a popup.
DismissPopups() {
    ; Loop a couple of times since these popups can re-fire instantly
    loop 3 {
        dismissed := false

        ; UIA-level: Bravo's "Till must be opened" / generic info dialog
        ; appears as an in-app modal with a "Ok" button AutoId=btnOk and a
        ; text element AutoId=txtMessage. Look for it and click Ok.
        try {
            root := GetBravoRoot()
            okBtn := 0
            try okBtn := root.FindElement({AutomationId: "btnOk"})
            if okBtn {
                okBtn.Click("left")
                LogMessage("    [popup] dismissed via btnOk")
                dismissed := true
                Sleep(400)
            }
        }

        ; Bravo's "Overdue Task Reminder" in-app modal — has Print All and
        ; Remind Me Later buttons. We never want to print mid-automation, so
        ; always click Remind Me Later to dismiss. This popup can appear at
        ; any time and block navigation if not handled.
        try {
            root := GetBravoRoot()
            remindBtn := 0
            try remindBtn := root.FindElement({Name: "Remind Me Later"})
            if remindBtn {
                remindBtn.Click("left")
                LogMessage("    [popup] dismissed Overdue Task Reminder via Remind Me Later")
                dismissed := true
                Sleep(500)
            }
        }

        ; "Information" dialog (Windows-level, separate from in-app modal)
        if WinExist("Information ahk_class") {
            try {
                WinActivate("Information ahk_class")
                Sleep(150)
                Send("{Enter}")
                dismissed := true
                Sleep(400)
            }
        }
        ; Same popup, sometimes appears with slightly different title format
        for hwnd in WinGetList() {
            try {
                title := WinGetTitle("ahk_id " . hwnd)
                if (title = "Information") {
                    WinActivate("ahk_id " . hwnd)
                    Sleep(150)
                    Send("{Enter}")
                    dismissed := true
                    Sleep(400)
                    break
                }
            }
        }

        ; "Overdue Task Reminder"
        if WinExist("Overdue Task Reminder") {
            try {
                WinActivate("Overdue Task Reminder")
                Sleep(150)
                Send("{Enter}")
                dismissed := true
                Sleep(400)
            }
        }

        if !dismissed
            break  ; nothing to dismiss this pass — exit loop
    }
}

; ----- Navigation ------------------------------------------------------------

; Return to the Dashboard from any working view by repeatedly clicking the
; right-panel "Done" button (AutomationId btnDone) until the Dashboard's
; right-sidebar Reports tree-view item is visible — that's the canonical
; "we're on the Dashboard" signal.
;
; The Dashboard does not expose btnDone, so once it stops appearing we know
; we're home. Bounded to maxHops to avoid infinite loops if something
; unexpected is on screen.
BackToDashboard(maxHops := 6) {
    if !ActivateBravo()
        return false
    DismissPopups()

    ; First, give the Dashboard up to 6 seconds to render on its own — common
    ; case after a fresh login where Reports sidebar takes a beat to populate.
    ; Avoids accidentally Esc'ing out of a Dashboard that simply hadn't drawn
    ; yet. (Esc on freshly-authenticated Bravo can drop back to Session List.)
    if FindByName("Reports", 6000) {
        LogMessage("    [nav] BackToDashboard: on Dashboard (initial wait)")
        return true
    }

    loop maxHops {
        ; "On Dashboard" signal: the sidebar Reports tree view item is present.
        onDash := ExistsByName("Reports")
        if onDash {
            LogMessage("    [nav] BackToDashboard: on Dashboard")
            return true
        }
        ; CHECK FIRST for an open modal dialog (Export Document, etc.) - those
        ; block any underlying Done click. Dismiss with Cancel. Order matters:
        ; modal dialog > Done > view Cancel button > (no Esc fallback - dangerous post-login).
        cancelElem := 0
        try cancelElem := GetBravoRoot().FindElement({AutomationId: "PART_CancelDialogButton"})
        if cancelElem {
            try {
                cancelElem.Click("left")
                LogMessage("    [nav] BackToDashboard: clicked DevExpress modal Cancel (PART_CancelDialogButton)")
            }
            Sleep(800)
            DismissPopups()
            continue
        }

        ; Bravo's own Custom Reports / Confirm dialogs use btnCancel AutoId.
        cancelElem := 0
        try cancelElem := GetBravoRoot().FindElement({AutomationId: "btnCancel"})
        if cancelElem {
            try {
                cancelElem.Click("left")
                LogMessage("    [nav] BackToDashboard: clicked Bravo dialog Cancel (btnCancel)")
            }
            Sleep(1200)
            DismissPopups()
            continue
        }

        ; Exit the underlying view. Try the right-panel Done button FIRST:
        ; item/list/detail views (e.g. Inventory) exit via Done, and a Cancel
        ; element is often ALSO present there but does NOT close the view, so
        ; clicking Cancel loops forever (2026-06-16 fix). Report-generator
        ; dialogs have no Done and are handled by btnCancel above.
        doneElem := 0
        try doneElem := GetBravoRoot().FindElement({AutomationId: "btnDone"})
        if doneElem {
            try {
                doneElem.Click("left")
                LogMessage("    [nav] BackToDashboard: clicked Done (btnDone)")
            }
            Sleep(1200)
            DismissPopups()
            continue
        }
        doneByName := FindByName("Done", 0)
        if doneByName {
            try {
                doneByName.Click("left")
                LogMessage("    [nav] BackToDashboard: clicked Done (Name)")
            }
            Sleep(1200)
            DismissPopups()
            continue
        }
        ; Fall back to a Cancel button by Name (report dialogs; right-panel red
        ; Cancel on Loans/Buys / Layaways / Customers views).
        cancelBtn := FindByName("Cancel", 0)
        if cancelBtn {
            try {
                cancelBtn.Click("left")
                LogMessage("    [nav] BackToDashboard: clicked Cancel (Name)")
            }
            Sleep(1200)
            DismissPopups()
            continue
        }
        ; No modal, no Done button, no Reports - just wait a bit longer
        ; rather than sending Esc. Bravo's freshly-rendered Dashboard can
        ; lag the Reports element by a few seconds.
        LogMessage("    [nav] BackToDashboard: waiting for Dashboard to render")
        Sleep(2000)
        DismissPopups()
    }

    ; ---- Esc fallback (added 2026-05-23) ----------------------------------
    ; Hops exhausted with no recovery. Previously we refused Esc here because
    ; on a freshly-authenticated Bravo it can drop to Session List. But we're
    ; already in a worse state — none of the known recovery elements were
    ; found for 6 iterations. If Esc lands us on Session List or Login, the
    ; next EnsureStore call detects via IsOnLoginScreen() and RecoverFromAutoLock
    ; logs us back in cleanly.
    LogMessage("    [nav] BackToDashboard: hops exhausted; trying Esc fallback (3x)")
    loop 3 {
        Send("{Escape}")
        Sleep(800)
    }
    DismissPopups()
    if FindByName("Reports", 4000) {
        LogMessage("    [nav] BackToDashboard: recovered via Esc fallback")
        return true
    }

    ; Still off-Dashboard. Take a screenshot so we can see WHAT Bravo
    ; was sitting on and fix the recovery list in a follow-up.
    try ScreenshotToFile("backtodashboard-unknown-state")
    return ExistsByName("Reports")
}


; ---------------------------------------------------------------------------
; ScreenshotToFile(tag) — full-screen PNG to <logsDir>\<logBase>_<tag>.png
;
; Uses the same PowerShell pattern as screenshot_bravo.bat. Saves a PNG
; alongside the per-run log so when EnsureStore / BackToDashboard fails
; we can SEE what Bravo was actually showing. Added 2026-05-23 because
; today's failure ("waiting for Dashboard to render" x6, then Lock Session
; click failed) gave us no signal at all about what state the UI was in.
;
; Safe to call from any failure path. Falls back to a log line on error.
; ---------------------------------------------------------------------------
ScreenshotToFile(tag) {
    global BRAVO_LOG_PATH
    if (BRAVO_LOG_PATH = "")
        return
    SplitPath BRAVO_LOG_PATH, , &logsDir, , &logBase
    pngPath := logsDir . "\" . logBase . "_" . tag . ".png"
    pngEsc := StrReplace(pngPath, "'", "''")
    ; Outer string is AHK double-quoted so we can use literal single quotes inside
    ; for PowerShell. The two `\"` sequences escape the outer PowerShell `-Command` quotes.
    ; Inside the PowerShell command, paths use PowerShell single-quote strings — 
    ; pngEsc already has any embedded `'` doubled per PowerShell escape rules.
    cmd := "powershell -NoProfile -WindowStyle Hidden -Command `"Add-Type -AssemblyName System.Windows.Forms; Add-Type -AssemblyName System.Drawing; $b = New-Object System.Drawing.Bitmap([System.Windows.Forms.SystemInformation]::VirtualScreen.Width, [System.Windows.Forms.SystemInformation]::VirtualScreen.Height); $g = [System.Drawing.Graphics]::FromImage($b); $g.CopyFromScreen([System.Windows.Forms.SystemInformation]::VirtualScreen.Location, [System.Drawing.Point]::Empty, $b.Size); $b.Save('" . pngEsc . "', 'Png'); $g.Dispose(); $b.Dispose()`""
    try {
        RunWait(cmd, , "Hide")
        LogMessage("    [screenshot] saved " . pngPath)
    } catch as e {
        LogMessage("    [screenshot] failed: " . e.Message)
    }
}

; ----- Logging ---------------------------------------------------------------

; Initialize per-run log file at <logsDir>\<triggerId>.log
InitLog(logsDir, triggerId) {
    global BRAVO_LOG_PATH
    BRAVO_LOG_PATH := logsDir . "\" . triggerId . ".log"
    LogMessage("=== Run started: " . triggerId . " ===")
}

LogMessage(msg) {
    global BRAVO_LOG_PATH
    line := FormatTime(, "yyyy-MM-dd HH:mm:ss") . " " . msg . "`r`n"
    if (BRAVO_LOG_PATH != "") {
        try FileAppend(line, BRAVO_LOG_PATH, "UTF-8")
    }
    ; Also write to OutputDebug so we can see it in DebugView while testing
    OutputDebug(line)
}

; ----- CSV writing -----------------------------------------------------------

; Quote a single CSV field if it contains comma, quote, or newline.
ToCsvField(value) {
    s := String(value)
    if RegExMatch(s, "[,`"`r`n]") {
        s := '"' . StrReplace(s, '"', '""') . '"'
    }
    return s
}

; Write a single CSV row to a file. Creates the file if missing.
WriteCsvRow(filepath, fields*) {
    row := ""
    for i, f in fields {
        if (i > 1)
            row .= ","
        row .= ToCsvField(f)
    }
    row .= "`r`n"
    FileAppend(row, filepath, "UTF-8-RAW")
}

; ----- Misc helpers ----------------------------------------------------------

; Build the canonical output filename for a (date, store, report) cell.
; date is "YYYY-MM-DD", store is the 3-letter code, reportSlug is e.g.
; "safe-register-journal". Returns just the filename (caller prepends dir).
OutputFilename(date, store, reportSlug) {
    return date . "_" . store . "_" . reportSlug . ".csv"
}

; Idempotency: delete an existing output file before re-running a cell so the
; new content fully replaces the old. The skill file requires this.
ResetOutputFile(filepath) {
    if FileExist(filepath) {
        try FileDelete(filepath)
    }
}
