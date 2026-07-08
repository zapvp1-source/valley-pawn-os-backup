; ============================================================================
; reports/SafeRegisterJournal_island.ahk  (slice 3 / UIA-v2 + CS-toggle patch)
;
; ISLAND VARIANT — clone of prod SafeRegisterJournal.ahk with two additive
; fixes that close the failure modes observed during the 2026-06-06 funds
; verification run (HAR / CUL / ROA all timed out with
; "Preview did not render within 30s (Export Document button never appeared)"
; before eventually succeeding on retry):
;
;   1. Preview-render wait bumped from 30s → 60s. The CS-on render frequently
;      pushes past 30s on wide reports; 60s matches the DepositsAndPaidOuts
;      and DisbursementJournal handlers that were patched 2026-05-29.
;
;   2. Continuous Scrolling toggle-off block ported in verbatim from
;      DepositsAndPaidOuts.ahk. SafeRegisterJournal was the ONLY export
;      handler in reports/ that never got the 2026-05-29 CS-toggle fix.
;      With CS still on, Bravo renders the whole report as one canvas and
;      the UIA tree becomes unresponsive — exactly the
;      "cannot get Bravo root: (0x800705B4) timeout" lines logged during
;      every failed cell on 2026-06-07.
;
; Deployment: drop ;_island suffix, copy to Bravo Data Extraction/reports/,
; reload watcher. No dispatch table change needed — same cell name. See
; island/proof-of-concept/safe-register-journal-cs-fix.md for the full
; checklist.
;
; Pulls Bravo's "Safe Register Journal" report for a single store and a
; single Business Date, exports it as CSV directly to our output folder,
; and returns a result Map.
;
; FLOW:
;   1. Bravo must be on the Dashboard for the right store.
;   2. Click "Reports" in the right sidebar.
;   3. In the Reports listing, click "Safe Register Journal" tile.
;   4. Click "Preview" in the right panel.
;   5. In the "Safe Register Journal Report Configuration" dialog, set the
;      Business Date and click Ok.
;   6. DevExpress Report Preview renders.
;   7. Click "Export Document..." in the toolbar.
;   8. In the Export Document dialog:
;        - Set Export format to Csv
;        - Set File path to our canonical output path
;        - Uncheck "Open file after exporting"
;        - Click OK
;   9. Click "Done" twice to return to the Dashboard.
;
; Slice 3: every click is a UIA element lookup. No more captured coordinates,
; no DPI scaling, no Mac chrome offsets. If a step throws, it means the UIA
; Name below doesn't match what Bravo actually exposes — drop a uia-discover
; trigger on that screen, find the right Name, update the constant here.
; ============================================================================

#Requires AutoHotkey v2.0

; ----- UIA element Names -----------------------------------------------------
; These are best-guess starting points. Verify with UIADiscover on each screen
; before declaring victory.

global SRJ_ELEMENTS := Map(
    "sidebar_reports",         "Reports",                  ; right-sidebar item (verify)
    "report_tile",             "Safe Register Journal",    ; tile in Reports listing
    "preview_button",          "Preview",                  ; right panel
    "config_business_date",    "Business Date",            ; label text (Edit may be sibling)
    "config_ok",               "Ok",                       ; config dialog OK
    "preview_export",          "Export...",                ; DevExpress menu item (verified via UIADiscover 2026-05-12)
    "export_format_combo",     "Export format",            ; verified - lowercase f
    "export_format_value",     "Csv",                      ; combo item
    "export_file_path",        "File path",                ; verified - lowercase p
    "export_open_after",       "Open file after exporting", ; verified - no leading "the"
    "export_ok",               "OK",                       ; AutoId=PART_OKDialogButton
    "panel_done",              "Done"                      ; right panel Done
)

; ----- Public entry point ----------------------------------------------------

PullSafeRegisterJournal(store, date, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "safe-register-journal",
        "store",       store,
        "date",        date,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    outputPath := outputDir . "\" . OutputFilename(date, store, "safe-register-journal")
    LogMessage("[" . store . "] SafeRegisterJournal date=" . date . " -> " . outputPath)

    ; --- Pre-flight ---
    if !WaitForBravoReady(30)
        return Fail(result, started, "Bravo window not found/ready within 30s")
    ActivateBravo()
    DismissPopups()

    ; Ensure we're on the target store. EnsureStore is a no-op if we're
    ; already there; otherwise it drives the full cycle.
    global CONFIG
    password := CONFIG.Has("bravo.password") ? CONFIG["bravo.password"] : ""
    if !EnsureStore(store, password)
        return Fail(result, started, "EnsureStore failed for " . store)
    LogMessage("  store confirmed: " . store)

    ResetOutputFile(outputPath)

    ; Pre-flight: make sure we're on the Dashboard (a previous run may have
    ; left Bravo in a Report Preview / Reports listing / Login Error / etc.).
    ; BackToDashboard clicks Done until the right-sidebar Reports item appears.
    if !BackToDashboard()
        return Fail(result, started, "BackToDashboard could not return Bravo to Dashboard")
    Sleep(500)
    DismissPopups()

    ; Wrap the click sequence in a try so any UIA lookup failure produces a
    ; clean error message in the result, not a crashed handler.
    try {
        ; Dismiss any in-app modal (e.g. "Till must be opened to complete a
        ; transaction") before driving the first nav click.
        DismissPopups()

        ; --- Step 1: open Reports listing ---
        LogMessage("  step 1: open Reports")
        ClickByName(SRJ_ELEMENTS["sidebar_reports"], 8000)
        Sleep(1500)
        DismissPopups()  ; popup can re-fire after each nav click

        ; --- Step 2+3: double-click Safe Register Journal tile to trigger Preview ---
        ; The right-panel "Preview" label is a custom WPF visual that doesn't
        ; expose a UIA-clickable element. Standard list-view behavior: double-
        ; click on the report row invokes the default action, which is Preview.
        LogMessage("  step 2: double-click report tile (= Preview)")
        DoubleClickByName(SRJ_ELEMENTS["report_tile"], 8000)
        Sleep(2500)
        DismissPopups()

        ; --- Step 4: config dialog — set Business Date and click Ok ---
        LogMessage("  step 4: set Business Date")
        SetBusinessDateUIA(date)
        Sleep(400)
        LogMessage("  step 4: click config Ok")
        ClickByName(SRJ_ELEMENTS["config_ok"], 5000)

        ; --- Step 5: wait for DevExpress preview to render ---
        ; The Export button is only present once the preview has rendered, so
        ; we can wait for it explicitly instead of a fixed sleep.
        ; PATCH 2026-06-08 (island): 30s → 60s. Matches DepositsAndPaidOuts /
        ; DisbursementJournal handlers patched 2026-05-29. CS-on renders
        ; routinely push past 30s on Safe Register Journal across stores.
        if !FindByName(SRJ_ELEMENTS["preview_export"], 60000)
            throw Error("Preview did not render within 60s (Export Document button never appeared)")
        Sleep(800)

        ; --- Step 5b: turn off Continuous Scrolling (added 2026-06-08 island) -----
        ; Bravo's Report Preview has an "Enable Continuous Scrolling" toggle
        ; that, when pressed, forces the entire report to render as one giant
        ; canvas. For multi-page Safe Register Journals, this freezes Bravo
        ; long enough that the UIA tree returns 0x800705B4 timeouts and the
        ; subsequent Export click lands on a still-rendering UI. Toggle state
        ; resets to ON on every Bravo restart per skill memory, so we always
        ; check-and-flip. Wrapped so it can't itself throw.
        ; Block ported verbatim from reports/DepositsAndPaidOuts.ahk (the
        ; canonical 2026-05-29 fix; SRJ never got it).
        try {
            csButton := FindByName("Enable Continuous Scrolling", 1000)
            if (csButton) {
                state := 0
                try state := csButton.TogglePattern.CurrentToggleState
                if (state = 1) {  ; UIA.ToggleState.On
                    LogMessage("    [pre-export] Continuous Scrolling is ON — calling Toggle() to flip state")
                    ; Use TogglePattern.Toggle() directly — Click("left") was a physical mouse
                    ; click at element center which often didn't actually toggle the CheckBox
                    ; in Bravo's WPF preview ribbon.
                    try csButton.TogglePattern.Toggle()
                    Sleep(2500)
                    ; verify the toggle actually flipped — if still on, try once more
                    newState := state
                    try newState := csButton.TogglePattern.CurrentToggleState
                    if (newState = 1) {
                        LogMessage("    [pre-export] WARN: first Toggle() didn't flip; retrying via Click()")
                        try csButton.Click("left")
                        Sleep(2500)
                        try newState := csButton.TogglePattern.CurrentToggleState
                    }
                    LogMessage("    [pre-export] post-toggle state = " . newState . " (0=Off)")
                    Sleep(3000)  ; give Bravo time to re-paginate after toggle
                } else {
                    LogMessage("    [pre-export] Continuous Scrolling already OFF (state=" . state . ")")
                }
            } else {
                LogMessage("    [pre-export] Continuous Scrolling button not found — skipping")
            }
        } catch as e {
            LogMessage("    [pre-export] WARN: Continuous Scrolling toggle-off failed: " . e.Message)
        }

        ; --- Step 6: Export ---
        LogMessage("  step 6: click Export Document")
        ClickByName(SRJ_ELEMENTS["preview_export"], 5000)
        ; Export Document dialog should appear; wait for it via the OK button.
        if !FindByName(SRJ_ELEMENTS["export_ok"], 8000)
            throw Error("Export Document dialog did not appear within 8s")

        ; --- Steps 7-10: drive the Export Document dialog via UIA patterns ---
        ; Robust setters (instead of the keyboard type-ahead that didn't stick
        ; in slice3-srj-cul-13). Each setter has graceful fallback and logs
        ; what it's doing - so on any failure the log + diagnostic dump tells
        ; us exactly which step needs adjustment.
        Sleep(800)

        ; Diagnostic: enumerate everything on the Export Document dialog before
        ; we try to set values. First successful run can remove this; while we
        ; iterate it's free reconnaissance.
        LogMessage("  step 7-pre: dumping Export Document dialog tree")
        LogVisibleNames(80)

        ; Step 7: Format = Csv (combobox)
        LogMessage("  step 7: set Export format = Csv (combobox expand+select)")
        SetExportFormatCsv()

        ; Step 8: File path
        LogMessage("  step 8: set File path = " . outputPath)
        SetExportFilePath(outputPath)

        ; Step 9: Uncheck "Open file after exporting"
        LogMessage("  step 9: uncheck open-after-export")
        UncheckOpenAfterExport()

        ; --- Step 10: OK to export ---
        LogMessage("  step 10: click export OK")
        ClickByName(SRJ_ELEMENTS["export_ok"], 5000)

        ; --- Step 11: wait for file to appear ---
        if !WaitForFile(outputPath, 30)
            throw Error("CSV file did not appear at " . outputPath . " within 30s")
        Sleep(500)

        ; --- Step 12: Done twice (exit preview, exit Reports list) ---
        LogMessage("  step 12: Done (exit preview)")
        try ClickByName(SRJ_ELEMENTS["panel_done"], 3000)
        Sleep(800)
        LogMessage("  step 12: Done (exit reports list)")
        try ClickByName(SRJ_ELEMENTS["panel_done"], 3000)
        Sleep(800)

    } catch as e {
        ; Failed mid-flow. Log every named clickable on the current screen so we
        ; can diagnose without re-running uia-discover separately.
        LogVisibleNames()
        return Fail(result, started, "UIA click sequence failed: " . e.Message)
    }

    ; --- Done ---
    rowCount := CountCsvRows(outputPath)
    result["row_count"]   := rowCount
    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: " . rowCount . " rows, " . result["duration_ms"] . "ms")
    return result
}

; ----- Helpers ---------------------------------------------------------------

; Set the Business Date field in the config dialog via UIA.
; Trigger format is YYYY-MM-DD; Bravo wants M/D/YYYY (e.g. "5/12/2026").
SetBusinessDateUIA(yyyymmdd) {
    parts := StrSplit(yyyymmdd, "-")
    if (parts.Length != 3) {
        LogMessage("  WARN: malformed date " . yyyymmdd . " — leaving Business Date at default")
        return
    }
    y := parts[1]
    m := Integer(parts[2])
    d := Integer(parts[3])
    bravoDate := m . "/" . d . "/" . y

    ; The Business Date field's UIA Name is most often the label text. If
    ; setting Value directly fails, SetValueByName falls back to focus +
    ; clipboard paste.
    SetValueByName(SRJ_ELEMENTS["config_business_date"], bravoDate, 5000)
    Sleep(150)
    Send("{Tab}")  ; commit
    Sleep(150)
}

; ----- Export Document dialog setters ---------------------------------------
;
; The DevExpress Export Document dialog has nested LayoutItem wrappers, so
; ValuePattern on the named element ("Export format", "File path", etc.) often
; fails or doesn't trigger a real commit. These three helpers handle each
; field with the appropriate UIA pattern and graceful fallbacks.

; Set the Export format combobox to "Csv". Strategy:
;   1. Find combobox by Name "Export format" (or by Type if naming fails).
;   2. Try ExpandCollapsePattern.Expand() to open the dropdown.
;   3. Click the "Csv" item by Name in the expanded popup.
;   4. Fallback: focus combo, type "csv", press Enter.
; --- Helper: read combo value, tolerating UIA timing flakes ----------------
SecGetComboValue(combo) {
    v := ""
    try {
        v := combo.Value
    } catch {
        ; some DevExpress combos expose value only via TextEdit child
        try {
            inner := combo.FindElement({Type: "Edit"})
            if inner
                v := inner.Value
        }
    }
    return v
}

; Verify that a combo's value contains the target text (case-insensitive).
SecComboHasValue(combo, target) {
    v := SecGetComboValue(combo)
    return (StrLen(v) > 0 && InStr(v, target))
}

SetExportFormatCsv() {
    combo := FindExportField("Export format", "ComboBox")
    if !combo {
        LogMessage("    WARN: Export format combo not found via Name or Type")
        throw Error("SetExportFormatCsv: combo not found")
    }
    ; --- STRATEGY REORDER 2026-05-28 ------------------------------------
    ; The ORIGINAL Strategy 1 (physical click + ClickByName "Csv") worked
    ; intermittently. When it didn't, Bravo accepted OK click but silently
    ; failed to write a CSV (defaulting to a non-CSV format). The keyboard
    ; approach below is more reliable because:
    ;   - Focus → Alt+Down opens dropdown (OS-level event Bravo expects)
    ;   - Send("Csv") triggers Bravo's combo autocomplete to highlight CSV
    ;   - Enter commits the selection through Bravo's normal keyboard flow
    ; This bypasses the UIA tree's flaky ClickByName lookup.
    LogMessage("    [kbd] Strategy 1 (keyboard): focus combo, Alt+Down, Csv, Tab")
    ; CRITICAL FIX 2026-05-28 v2: Send("{Enter}") was closing the entire
    ; Export Document dialog (Enter = default OK button), so step 7's
    ; SetExportFilePath couldn't find the LayoutItem (dialog gone).
    ; Diagnosed by driving the dialog manually — confirmed that picking CSV
    ; from the dropdown does change format AND auto-updates the file path
    ; extension to .csv. So we just need to commit the dropdown selection
    ; without triggering OK. Tab moves focus to the next field (File path)
    ; which commits the dropdown selection AND keeps the dialog open.
    try {
        try combo.Focus()
        Sleep(300)
        Send("!{Down}")    ; Alt+Down opens the focused combo's dropdown
        Sleep(600)
        Send("Csv")        ; combo autocomplete highlights Csv item
        Sleep(400)
        Send("{Tab}")      ; commits selection AND keeps dialog open
        Sleep(1200)        ; give Bravo time to internally commit
        if SecComboHasValue(combo, "Csv") {
            LogMessage("    [kbd] Strategy 1 verified, Value=" . SecGetComboValue(combo))
            return true
        }
        LogMessage("    [verify] Strategy 1 (kbd) set but combo.Value='" . SecGetComboValue(combo) . "' — trying next strategy")
    } catch as e {
        LogMessage("    WARN keyboard strategy failed: " . e.Message)
    }
    ; --- Strategy 2 (legacy UIA click): physical click on combo, then
    ; ClickByName "Csv" in the expanded popup. Kept as fallback because it
    ; worked at 9:34 AM today.
    try {
        combo.Click("left")
        LogMessage("    [UIA] Export format combo physical-clicked")
        Sleep(500)
    } catch as e {
        LogMessage("    WARN combo physical click failed: " . e.Message)
    }
    try {
        ClickByName(SRJ_ELEMENTS["export_format_value"], 2500)
        Sleep(1200)        ; longer settle than before (was 400ms)
        if SecComboHasValue(combo, "Csv") {
            LogMessage("    [UIA] Export format Value=" . SecGetComboValue(combo) . " (verified)")
            return true
        }
        LogMessage("    [verify] Strategy 2 set but combo.Value='" . SecGetComboValue(combo) . "' — trying next strategy")
    } catch as e {
        LogMessage("    WARN ClickByName Csv after expand failed: " . e.Message)
    }
    ; Strategy 2: try ExpandCollapsePattern explicitly
    try {
        combo.ExpandCollapsePattern.Expand()
        Sleep(400)
        ClickByName(SRJ_ELEMENTS["export_format_value"], 2000)
        Sleep(400)
        if SecComboHasValue(combo, "Csv") {
            LogMessage("    [UIA] Export format set via ExpandCollapse, Value=" . SecGetComboValue(combo) . " (verified)")
            return true
        }
        LogMessage("    [verify] Strategy 2 set but combo.Value='" . SecGetComboValue(combo) . "' — trying next strategy")
    } catch as e {
        LogMessage("    WARN ExpandCollapse path failed: " . e.Message)
    }
    ; Strategy 3: drill into the combo's child Edit and set Value directly,
    ; then commit with Tab. DevExpress LookUpEdit exposes its inner Edit as
    ; a child with Name 'TextEdit' or AutoId PART_Editor.
    try {
        innerEdit := combo.FindElement({Type: "Edit"})
        if innerEdit {
            innerEdit.Value := "Csv"
            LogMessage("    [UIA] Export format inner Edit Value := Csv")
            try innerEdit.Focus()
            Sleep(150)
            Send("{Tab}")
            Sleep(400)
            if SecComboHasValue(combo, "Csv") {
                LogMessage("    [UIA] Strategy 3 verified, Value=" . SecGetComboValue(combo))
                return true
            }
            LogMessage("    [verify] Strategy 3 set but combo.Value='" . SecGetComboValue(combo) . "' — trying keyboard fallback")
        }
    } catch as e {
        LogMessage("    WARN inner Edit path failed: " . e.Message)
    }
    ; Strategy 4 (final fallback): keyboard. Focus combo, Alt+Down, type, Enter.
    try combo.Focus()
    Sleep(150)
    Send("!{Down}")  ; Alt+Down opens dropdown of focused combo
    Sleep(300)
    Send("Csv")
    Sleep(200)
    Send("{Enter}")
    Sleep(400)
    if SecComboHasValue(combo, "Csv") {
        LogMessage("    [kbd] Export format set via keyboard, Value=" . SecGetComboValue(combo) . " (verified)")
        return true
    }
    ; All four strategies completed but combo.Value still reads empty. NOTE
    ; (revised 2026-05-28): the working 09:34 EOM run ALSO logged Value=''
    ; and exported successfully — so combo.Value is unreliable as a verifier
    ; for THIS DevExpress combo. We can't tell from combo.Value alone whether
    ; the format actually stuck. Strategy: log a warning, give Bravo extra
    ; time to internally commit, then proceed (caller will add its own
    ; pre-OK sleep). Throwing here would cause false-negatives.
    LogMessage("    [verify] All 4 strategies completed, combo.Value unreadable ('') — proceeding with extra settle time")
    Sleep(1500)
    return true
}

; Set the File path field. The dialog wraps the actual Edit inside a LayoutItem
; whose Name="File path". ValuePattern on the wrapper doesn't write the inner
; Edit, so we descend to the child Edit (AutoId=PART_Editor or first Edit child)
; and set its value directly.
; Verify the file path Edit's value matches the target. Tolerates whitespace
; and case differences in the Bravo edit (some DevExpress edits normalize).
SecVerifyEditValue(edit, expected) {
    actual := ""
    try actual := edit.Value
    if (StrLen(actual) = 0)
        return false
    ; Match if expected appears in actual or vice versa (path may be normalized)
    return (InStr(actual, expected) || InStr(expected, actual))
}

SetExportFilePath(outputPath) {
    layout := FindByName(SRJ_ELEMENTS["export_file_path"], 2000)
    if !layout {
        LogMessage("    WARN: File path LayoutItem not found by Name")
        throw Error("SetExportFilePath: File path LayoutItem not found")
    }
    ; Look for a child Edit (the actual text entry).
    edit := 0
    try {
        edit := layout.FindElement({Type: "Edit"})
    } catch as e {
        LogMessage("    WARN: could not enumerate Edit children: " . e.Message)
    }
    if edit {
        try {
            edit.Value := outputPath
            LogMessage("    [UIA] File path child Edit Value set directly")
            ; Tab off to commit
            try edit.Focus()
            Sleep(100)
            Send("{Tab}")
            Sleep(400)
            ; --- VERIFY (added 2026-05-28) -----------------------------------
            if SecVerifyEditValue(edit, outputPath) {
                LogMessage("    [UIA] File path verified: '" . edit.Value . "'")
                return true
            }
            LogMessage("    [verify] File path set but Edit.Value='" . edit.Value . "' — trying fallback")
        } catch as e {
            LogMessage("    WARN: child Edit ValuePattern failed: " . e.Message)
        }
    }
    ; Fallback: clipboard paste into the named layout target.
    try {
        SetValueByName(SRJ_ELEMENTS["export_file_path"], outputPath, 2000)
        Sleep(200)
        Send("{Tab}")
        Sleep(400)
        ; Re-find the edit and verify the fallback worked (advisory only —
        ; the Edit's Value may not be readable via UIA even when set).
        try {
            layout2 := FindByName(SRJ_ELEMENTS["export_file_path"], 1000)
            edit2 := layout2 ? layout2.FindElement({Type: "Edit"}) : 0
            if edit2 && SecVerifyEditValue(edit2, outputPath) {
                LogMessage("    [UIA] File path fallback verified: '" . edit2.Value . "'")
                return true
            }
            LogMessage("    [verify] File path fallback set but Value unreadable — proceeding with extra settle time")
        }
        Sleep(1000)
        return true
    } catch as e {
        LogMessage("    WARN: SetExportFilePath fallback path: " . e.Message . " — proceeding")
        Sleep(500)
        return true
    }
}

; Uncheck "Open file after exporting". Strategy:
;   1. Try FindByName, then TogglePattern.
;   2. If not found by Name, walk all CheckBox elements and match by Name substring.
;   3. Last resort: keyboard Space on whatever currently has focus.
UncheckOpenAfterExport() {
    elem := FindByName(SRJ_ELEMENTS["export_open_after"], 1500)
    if !elem {
        ; Try a broader CheckBox sweep
        try {
            root := GetBravoRoot()
            checks := root.FindElements({Type: "CheckBox"})
            for c in checks {
                try {
                    n := c.Name
                } catch {
                    continue
                }
                if InStr(n, "Open file") {
                    elem := c
                    LogMessage("    [UIA] open-after-export matched by substring: '" . n . "'")
                    break
                }
            }
        } catch as e {
            LogMessage("    WARN: CheckBox sweep failed: " . e.Message)
        }
    }
    if !elem {
        LogMessage("    WARN: open-after-export not found; skipping uncheck")
        return false
    }
    ; Read current state and toggle if needed
    try {
        state := elem.ToggleState  ; 0 = off, 1 = on
        if (state = 0) {
            LogMessage("    [UIA] open-after-export already off")
            return true
        }
        try elem.TogglePattern.Toggle()
        Sleep(400)
        ; --- VERIFY (added 2026-05-28) -----------------------------------
        ; Read state back; if still on, retry once.
        try {
            postState := elem.ToggleState
            if (postState = 0) {
                LogMessage("    [UIA] open-after-export toggled off (verified)")
                return true
            }
            LogMessage("    [verify] Toggle didn't take, state=" . postState . " — retrying via click")
        }
        try elem.Click("left")
        Sleep(400)
        try {
            finalState := elem.ToggleState
            if (finalState = 0) {
                LogMessage("    [UIA] open-after-export off after Click retry (verified)")
                return true
            }
            LogMessage("    [verify] Click retry didn't take either, state=" . finalState)
        }
        ; If we get here, both toggle and click failed to flip the state.
        ; "Open after export" being ON would just open Excel/whatever after
        ; the CSV writes — annoying but doesn't hang Bravo. Log and continue
        ; (don't throw — the Open-After flag isn't the cause of the hang
        ; we're fixing).
        LogMessage("    WARN: open-after-export could not be unchecked but proceeding (not a hang risk)")
        return false
    } catch as e {
        ; Fallback: click directly
        try {
            elem.Click("left")
            LogMessage("    [UIA] open-after-export Click() fallback")
            Sleep(400)
            try {
                if (elem.ToggleState = 0) {
                    LogMessage("    [UIA] open-after-export off after Click fallback (verified)")
                    return true
                }
            }
            LogMessage("    WARN: open-after-export Click fallback didn't verify but proceeding")
            return false
        } catch as e2 {
            LogMessage("    ERROR: open-after-export toggle + click both failed: " . e2.Message)
            return false
        }
    }
}

; Internal - find an Export dialog field by Name; fall back to first element
; of the given Type. Returns 0 if nothing found.
FindExportField(name, typeName) {
    elem := FindByName(name, 1500)
    if elem
        return elem
    try {
        elem := GetBravoRoot().FindElement({Type: typeName})
    } catch {
        return 0
    }
    if elem
        LogMessage("    [UIA] " . name . " not found by Name; using first " . typeName)
    return elem
}

WaitForFile(path, timeoutSec) {
    deadline := A_TickCount + timeoutSec * 1000
    loop {
        if FileExist(path) {
            size1 := FileGetSize(path)
            Sleep(400)
            size2 := FileGetSize(path)
            if (size1 = size2 and size1 > 0)
                return true
        }
        if (A_TickCount > deadline)
            return false
        Sleep(400)
    }
}

CountCsvRows(csvPath) {
    if !FileExist(csvPath)
        return 0
    count := 0
    loop read csvPath {
        count++
    }
    return Max(0, count - 1)
}

Fail(result, started, msg) {
    result["error"] := msg
    result["duration_ms"] := A_TickCount - started
    LogMessage("  ERROR: " . msg)
    return result
}
