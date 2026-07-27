#!/usr/bin/env python3
"""Patch IntakeDetail.ahk: popup-editor date fallback + clean exit on error.

Root cause (2026-06-12): on LEX/WAY the loaded saved report's date criteria
cells expose as PopupBaseEdit (PART_Editor) instead of BravoDateEdit, so
SetReportDate throws. The error path then left the Loans/Buys screen open,
which blocked the next store switch ("Cannot switch stores: FREE1 is busy").
"""
import sys

PATH = "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/reports/IntakeDetail.ahk"

src = open(PATH, encoding="utf-8").read()
orig = src

EM = "—"  # em dash used in existing strings

# --- 1. Start Date fallback --------------------------------------------------
old_start = (
    '        try {\n'
    '            SetReportDate(1, startDate)\n'
    '        } catch as e {\n'
    '            LogMessage("    WARN: SetReportDate(1) failed: " . e.Message)\n'
    '            LogVisibleNames()\n'
    f'            throw Error("Could not set Start Date {EM} see LogVisibleNames dump")\n'
    '        }\n'
)
new_start = (
    '        try {\n'
    '            SetReportDate(1, startDate)\n'
    '        } catch as e {\n'
    '            LogMessage("    WARN: SetReportDate(1) failed: " . e.Message . " - trying popup-editor fallback")\n'
    '            try {\n'
    '                IntakeSetDateByPopupEditor(1, startDate)\n'
    '            } catch as e2 {\n'
    '                LogMessage("    WARN: popup-editor fallback(1) failed: " . e2.Message)\n'
    '                LogVisibleNames()\n'
    f'                throw Error("Could not set Start Date {EM} see LogVisibleNames dump")\n'
    '            }\n'
    '        }\n'
)
if old_start not in src:
    sys.exit("FAIL: start-date block not found")
src = src.replace(old_start, new_start)

# --- 2. End Date fallback ----------------------------------------------------
old_end = (
    '        try {\n'
    '            SetReportDate(2, endDate)\n'
    '        } catch as e {\n'
    '            LogMessage("    WARN: SetReportDate(2) failed: " . e.Message)\n'
    '            LogVisibleNames()\n'
    f'            throw Error("Could not set End Date {EM} see LogVisibleNames dump")\n'
    '        }\n'
)
new_end = (
    '        try {\n'
    '            SetReportDate(2, endDate)\n'
    '        } catch as e {\n'
    '            LogMessage("    WARN: SetReportDate(2) failed: " . e.Message . " - trying popup-editor fallback")\n'
    '            try {\n'
    '                IntakeSetDateByPopupEditor(2, endDate)\n'
    '            } catch as e2 {\n'
    '                LogMessage("    WARN: popup-editor fallback(2) failed: " . e2.Message)\n'
    '                LogVisibleNames()\n'
    f'                throw Error("Could not set End Date {EM} see LogVisibleNames dump")\n'
    '            }\n'
    '        }\n'
)
if old_end not in src:
    sys.exit("FAIL: end-date block not found")
src = src.replace(old_end, new_end)

# --- 3. Clean exit on error ----------------------------------------------------
old_catch = (
    '    } catch as e {\n'
    '        LogVisibleNames()\n'
    '        return Fail(result, started, "UIA click sequence failed: " . e.Message)\n'
    '    }\n'
)
new_catch = (
    '    } catch as e {\n'
    '        LogVisibleNames()\n'
    '        ; Close the Loans/Buys screen before failing - a leftover open screen\n'
    '        ; blocks the next store switch ("Cannot switch stores: ... is busy\n'
    '        ; with Loans/Buys"), which cascades into EnsureStore failures.\n'
    '        IntakeCloseReportScreen()\n'
    '        return Fail(result, started, "UIA click sequence failed: " . e.Message)\n'
    '    }\n'
)
if old_catch not in src:
    sys.exit("FAIL: catch block not found")
src = src.replace(old_catch, new_catch)

# --- 4. Append helper functions ------------------------------------------------
helpers = '''

; ----------------------------------------------------------------------------
; 2026-06-12 fix: on some stores (observed LEX/WAY) the loaded saved report's
; Transaction Date criteria cells do NOT instantiate BravoDateEdit controls -
; they expose as PopupBaseEdit (AutoId=PART_Editor) until the cell is
; activated. Strategy: click the editor at the given x-position (1=start,
; 2=end) to activate it, retry the standard SetReportDate path, and if the
; control still is not a BravoDateEdit, set the popup editor directly via
; ValuePattern, then clipboard paste as last resort.
IntakeSetDateByPopupEditor(position, yyyymmdd) {
    parts := StrSplit(yyyymmdd, "-")
    if (parts.Length != 3)
        throw Error("malformed date " . yyyymmdd)
    bravoDate := Integer(parts[2]) . "/" . Integer(parts[3]) . "/" . parts[1]

    el := IntakeFindPopupDateEditor(position)
    if !el
        throw Error("no PopupBaseEdit PART_Editor found at position " . position)

    try el.Click("left")
    Sleep(500)

    ; Activation may have instantiated a real BravoDateEdit - retry standard path.
    try {
        SetReportDate(position, yyyymmdd)
        LogMessage("    [date-fallback] standard path succeeded after cell activation (position " . position . ")")
        return
    }

    ; Re-find: the reference can go stale after activation.
    el := IntakeFindPopupDateEditor(position)
    if !el
        throw Error("popup editor vanished after activation (position " . position . ")")

    try {
        el.Value := bravoDate
        Sleep(150)
        Send("{Tab}")
        Sleep(150)
        LogMessage("    [date-fallback] position=" . position . " set to " . bravoDate . " via ValuePattern")
        return
    } catch as e {
        LogMessage("    WARN [date-fallback] ValuePattern failed: " . e.Message . " - trying clipboard")
    }

    try el.Focus()
    Sleep(200)
    A_Clipboard := bravoDate
    ClipWait(2)
    Send("^a")
    Sleep(100)
    Send("^v")
    Sleep(200)
    Send("{Tab}")
    Sleep(150)
    LogMessage("    [date-fallback] position=" . position . " pasted via clipboard")
}

; Find the Nth (by x ascending) Edit named 'PopupBaseEdit' with
; AutomationId=PART_Editor. Returns the element or 0.
IntakeFindPopupDateEditor(position) {
    wrappers := []
    try {
        root := GetBravoRoot()
        edits := root.FindElements({Type: "Edit"})
        for e in edits {
            n := ""
            try n := e.Name
            if (n != "PopupBaseEdit")
                continue
            autoId := ""
            try autoId := e.AutomationId
            if (autoId != "PART_Editor")
                continue
            rect := 0
            try rect := e.BoundingRectangle
            if !rect
                continue
            wrappers.Push(Map("elem", e, "x", rect.l))
        }
    } catch as ex {
        LogMessage("    WARN IntakeFindPopupDateEditor: " . ex.Message)
        return 0
    }
    if (wrappers.Length < position)
        return 0
    ; selection sort by x ascending
    Loop wrappers.Length {
        i := A_Index
        minIdx := i
        j := i + 1
        while (j <= wrappers.Length) {
            if (wrappers[j]["x"] < wrappers[minIdx]["x"])
                minIdx := j
            j++
        }
        if (minIdx != i) {
            tmp := wrappers[i]
            wrappers[i] := wrappers[minIdx]
            wrappers[minIdx] := tmp
        }
    }
    return wrappers[position]["elem"]
}

; Best-effort: dismiss dialogs and close the Loans/Buys screen so a failed
; cell can never leave Bravo "busy with Loans/Buys" and block the next store.
IntakeCloseReportScreen() {
    try DismissPopups()
    Loop 2 {
        try ClickByName(INTAKE_ELEMENTS["panel_cancel"], 2000)
        Sleep(700)
    }
    try DismissPopups()
    try BackToDashboard()
    Sleep(500)
}
'''
src = src.rstrip("\n") + "\n" + helpers

open(PATH, "w", encoding="utf-8", newline="").write(src)
print("PATCH OK - %d -> %d chars" % (len(orig), len(src)))
