; ============================================================================
; set_dates_and_run.ahk
;
; Standalone AHK — assumes Bravo is showing the Custom Reports dialog with
; "Claude Inventory Details" loaded. Sets the Status Date filter range to
; START_DATE..END_DATE (constants below), then clicks the "Ok" Text element
; (which appears at ~(2677, 1686)) to run the report.
;
; Run via Session-1 scheduled task launcher.
; ============================================================================

#Requires AutoHotkey v2.0
#SingleInstance Force

#Include \\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\lib\UIA-v2\UIA.ahk

; Trailing 12-month window (matches buys data context)
START_DATE := "5/17/2025"
END_DATE   := "5/17/2026"

LOG_PATH := "\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\logs\set_dates_and_run.log"

LogMsg(msg) {
    line := FormatTime(, "yyyy-MM-dd HH:mm:ss") . " " . msg . "`r`n"
    try FileAppend(line, LOG_PATH, "UTF-8-RAW")
}

GetBravoRoot() {
    hwnd := WinExist("Bravo ")
    if !hwnd
        throw Error("Bravo window not found")
    return UIA.ElementFromHandle(hwnd)
}

; Find BravoDateEdit wrappers sorted by X coordinate. Position 1 = leftmost
; (Start Date), Position 2 = next (End Date). Returns inner PART_Editor child.
FindBravoDateEditByPosition(position) {
    wrappers := []
    try {
        root := GetBravoRoot()
        edits := root.FindElements({Type: "Edit"})
        for e in edits {
            n := ""
            try n := e.Name
            if (n != "BravoDateEdit")
                continue
            autoId := ""
            try autoId := e.AutomationId
            if (autoId = "PART_Editor")
                continue
            rect := 0
            try rect := e.BoundingRectangle
            if !rect
                continue
            wrappers.Push(Map("elem", e, "x", rect.l))
        }
    }
    ; Sort by x ascending
    n := wrappers.Length
    i := 2
    while (i <= n) {
        j := i
        while (j > 1 && wrappers[j]["x"] < wrappers[j-1]["x"]) {
            tmp := wrappers[j]
            wrappers[j] := wrappers[j-1]
            wrappers[j-1] := tmp
            j--
        }
        i++
    }
    if (position < 1 || position > wrappers.Length)
        return 0
    wrapper := wrappers[position]["elem"]
    try {
        inner := wrapper.FindElement({Type: "Edit"})
        if inner
            return inner
    }
    return wrapper
}

SetDate(position, dateStr) {
    edit := FindBravoDateEditByPosition(position)
    if !edit {
        LogMsg("WARN: BravoDateEdit position " . position . " not found")
        return false
    }
    try {
        edit.Value := dateStr
        LogMsg("set position " . position . " to " . dateStr . " via ValuePattern")
        Sleep(200)
        Send("{Tab}")
        Sleep(200)
        return true
    } catch as e {
        LogMsg("ValuePattern failed for position " . position . ": " . e.Message)
    }
    ; Fallback: focus + clipboard paste
    try edit.Focus()
    Sleep(200)
    A_Clipboard := dateStr
    ClipWait(2)
    Send("^a")
    Sleep(100)
    Send("^v")
    Sleep(200)
    Send("{Tab}")
    Sleep(200)
    LogMsg("set position " . position . " to " . dateStr . " via clipboard")
    return true
}

; Click the "Ok" Text element (it's a Text control, not a Button — that's why
; UIA Button searches missed it). Find by Name='Ok' in the dialog area
; (y > 1000 to avoid column-header 'Ok' elements).
ClickOkTextElement() {
    try {
        root := GetBravoRoot()
        texts := root.FindElements({Type: "Text"})
        for t in texts {
            n := ""
            try n := t.Name
            if (n != "Ok")
                continue
            rect := 0
            try rect := t.BoundingRectangle
            if !rect
                continue
            ; Skip Ok elements that are NOT in the dialog area (column headers)
            if (rect.t < 1000)
                continue
            cx := Integer(rect.l + rect.r) // 2
            cy := Integer(rect.t + rect.b) // 2
            LogMsg("found Ok text at (" . cx . "," . cy . ") — clicking")
            CoordMode "Mouse", "Screen"
            MouseClick("Left", cx, cy)
            return true
        }
    } catch as e {
        LogMsg("ClickOkTextElement failed: " . e.Message)
    }
    return false
}

LogMsg("=== set_dates_and_run.ahk started ===")
LogMsg("target dates: " . START_DATE . " to " . END_DATE)

try {
    WinActivate("Bravo ")
    WinWaitActive("Bravo ", , 5)
    Sleep(800)
}

if !SetDate(1, START_DATE)
    LogMsg("ERROR: failed to set Start Date")
Sleep(400)
if !SetDate(2, END_DATE)
    LogMsg("ERROR: failed to set End Date")
Sleep(800)

if !ClickOkTextElement()
    LogMsg("ERROR: failed to click Ok")
else
    LogMsg("Ok clicked — report should be running")

ExitApp(0)
