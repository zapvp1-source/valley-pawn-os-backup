; ============================================================================
; MobileEventsRead.ahk -- STANDALONE, READ-ONLY (added 2026-11-18, Joshua OK "lets proceed").
; Reads Customers > Schedule Mobile Event (Bravo's automatic text/push setup) in each store
; and writes what it shows to output\mobile_events\<STORE>.txt (+ .png). Nothing else.
;
; ADDITIVE: new file. Does not touch bravo_watcher.ahk, any handler, any saved report.
; SAFETY (hard rules):
;   - The only controls ever clicked: sidebar Customers, "Schedule Mobile Event", and the
;     editor's own button named exactly "Cancel". Never Ok, Save, Done-in-editor, a checkbox,
;     a text box, Add new event, Edit Recurrence, or a template button. No keystrokes are sent.
;   - If "Cancel" cannot be found the script stops with ABORT (the Mac wrapper runs the health gate).
;   - Yields (stops cleanly on a Dashboard) if the pipeline has a trigger waiting or just claimed.
; Args: <stores e.g. CUL,HAR,LEX,ROA,WAY>
; ASCII only.
; ============================================================================
#Requires AutoHotkey v2.0
#SingleInstance Force
#Warn All, Off
SetWorkingDir(A_ScriptDir)
#Include lib\_secrets.ahk
#Include lib\Json.ahk
#Include lib\Bravo.ahk
#Include lib\EnsureDashboard.ahk
#Include lib\StoreCycle.ahk

global CONFIG := Map()
CONFIG["bravo.username"] := "FREE1@WAY"
CONFIG["bravo.password"] := BRAVO_PASSWORD
CONFIG["paths.logs"]     := A_ScriptDir . "\logs"
global OUT_DIR     := A_ScriptDir . "\output\mobile_events"
global STATUS_FILE := OUT_DIR . "\_status.txt"
global STORES      := StrSplit((A_Args.Length >= 1) ? A_Args[1] : "WAY", ",")
global EDITOR_TEXT := "The enabled events below are scheduled to send a message to all mobile customers"
global DUMP_COUNT  := 0
global MODE        := (A_Args.Length >= 2) ? A_Args[2] : "events"
; templates mode (2026-11-18, Joshua "lets go on all three"): also click each reminder TEMPLATE button to read
; its wording, one button per editor visit, and leave every time by Cancel only.
global TPL_BUTTONS := ["Single Loan Courtesy Reminder", "Multiple Loan Courtesy Reminder", "Single Layaway Notice", "Multiple Layaway Notice", "Single Loan Past Due Reminder", "Multiple Loan Past Due Reminder"]
OnError(MerOnError)
MerMain()
ExitApp(0)

MerMain() {
    global
    if !DirExist(OUT_DIR)
        DirCreate(OUT_DIR)
    InitLog(A_ScriptDir . "\logs", "mobileevents-" . FormatTime(, "yyyy-MM-ddTHH-mm-ss"))
    MerStatus("STARTING")
    if !EnsureBravoDashboard(BRAVO_PASSWORD, STORES[1]) {
        MerStatus("ABORT no-dashboard-at-start")
        ExitApp(2)
    }
    done := ""
    for st in STORES {
        st := Trim(st)
        why := MerPipelineBusy()
        if (why != "") {
            MerStatus("PAUSED pipeline busy (" . why . ") done=" . done)
            ExitApp(0)
        }
        MerStatus("RUNNING " . st . " done=" . done)
        if !EnsureStore(st, BRAVO_PASSWORD) {
            LogMessage("could not reach store " . st . " - skipping")
            continue
        }
        Sleep(1500)
        DismissPopups()
        if (GetCurrentStoreCode() != st) {
            LogMessage("title bar is not " . st . " - skipping")
            continue
        }
        if (MODE = "templates") {
            for b in TPL_BUTTONS {
                if (MerPipelineBusy() != "")
                    break
                MerReadTemplate(st, b)
            }
            done .= st . " "
        } else if MerReadStore(st)
            done .= st . " "
    }
    try BackToDashboard()
    MerStatus("COMPLETE done=" . done)
}

MerReadStore(st) {
    root := GetBravoRoot()
    el := MerFind(root, {AutomationId: "Dashboard.Buttons.Customers"})
    if !el
        throw Error("Customers sidebar item not found")
    el.Click("left")
    Sleep(4000)
    DismissPopups()
    MerWaitNotHung(90)
    btn := MerFind(GetBravoRoot(), {Name: "Schedule Mobile Event", Type: "Button"})
    if !btn
        btn := MerFind(GetBravoRoot(), {Name: "Schedule Mobile Event"})
    if !btn
        throw Error("Schedule Mobile Event not found")
    btn.Click("left")
    Sleep(4500)
    MerWaitNotHung(90)
    if !ExistsByName(EDITOR_TEXT)
        Sleep(4000)
    opened := ExistsByName(EDITOR_TEXT)
    title := ""
    try title := WinGetTitle(BRAVO_WIN_TITLE)
    out := "# store: " . st . "`r`n# captured: " . FormatTime(, "yyyy-MM-dd HH:mm:ss") . "`r`n# title: " . title . "`r`n# editor_open: " . (opened ? "yes" : "NO") . "`r`n"
    out .= "# format: [type] N=name | C=class | R=l,t,r,b | TOGGLE=0/1 | V=value | TEXT=document text`r`n"
    if opened {
        DUMP_COUNT := 0
        try MerDump(GetBravoRoot(), 0, &out)
        MerShot(st)
    }
    MerWrite(OUT_DIR . "\" . st . ".txt", out)
    ; ---- leave by the editor's own Cancel, never anything else
    if opened {
        closed := false
        Loop 6 {
            ; UIA can time out (0x80131505) right after the big tree read; wait and retry, Cancel only
            try {
                c := MerFind(GetBravoRoot(), {Name: "Cancel", Type: "Button"})
                if c {
                    c.Click("left")
                    Sleep(2500)
                }
                if !ExistsByName(EDITOR_TEXT) {
                    closed := true
                    break
                }
            } catch as e {
                LogMessage("   cancel attempt " . A_Index . " error: " . e.Message)
            }
            Sleep(5000)
        }
        if !closed {
            MerStatus("ABORT editor-still-open " . st)
            ExitApp(4)
        }
    }
    ok := false
    try ok := BackToDashboard()
    if !ok {
        MerStatus("ABORT no-dashboard-after " . st)
        ExitApp(4)
    }
    return opened
}

MerOpenEditor() {
    el := MerFind(GetBravoRoot(), {AutomationId: "Dashboard.Buttons.Customers"})
    if !el
        throw Error("Customers sidebar item not found")
    el.Click("left")
    Sleep(4000)
    DismissPopups()
    MerWaitNotHung(90)
    btn := MerFind(GetBravoRoot(), {Name: "Schedule Mobile Event", Type: "Button"})
    if !btn
        throw Error("Schedule Mobile Event not found")
    btn.Click("left")
    Sleep(5000)
    MerWaitNotHung(90)
    if !ExistsByName(EDITOR_TEXT)
        Sleep(4000)
    return ExistsByName(EDITOR_TEXT)
}

; Cancel only, innermost first (separate dialog windows, then the main window), until the editor is gone.
MerCancelAll(st) {
    Loop 8 {
        try {
            mainHwnd := WinExist(BRAVO_WIN_TITLE)
            clicked := false
            for hwnd in WinGetList("ahk_exe Bravo.exe") {
                if (hwnd = mainHwnd || !DllCall("IsWindowVisible", "ptr", hwnd, "int"))
                    continue
                c := MerFind(UIA.ElementFromHandle(hwnd), {Name: "Cancel", Type: "Button"})
                if c {
                    c.Click("left")
                    clicked := true
                    Sleep(2000)
                    break
                }
            }
            if !clicked {
                if !ExistsByName(EDITOR_TEXT)
                    return true
                c := MerFind(GetBravoRoot(), {Name: "Cancel", Type: "Button"})
                if c {
                    c.Click("left")
                    Sleep(2500)
                }
            }
        } catch as e {
            LogMessage("   cancel-all attempt " . A_Index . " error: " . e.Message)
            Sleep(5000)
        }
    }
    if ExistsByName(EDITOR_TEXT) {
        MerStatus("ABORT editor-still-open " . st)
        ExitApp(4)
    }
    return true
}

MerReadTemplate(st, bname) {
    global DUMP_COUNT
    if !MerOpenEditor() {
        LogMessage("editor did not open for " . st . " / " . bname)
        try BackToDashboard()
        return false
    }
    slug := RegExReplace(bname, "[^A-Za-z0-9]+", "_")
    out := "# store: " . st . "`r`n# template button: " . bname . "`r`n# captured: " . FormatTime(, "yyyy-MM-dd HH:mm:ss") . "`r`n"
    b := MerFind(GetBravoRoot(), {Name: bname, Type: "Button"})
    if !b {
        out .= "# BUTTON NOT FOUND`r`n"
    } else {
        try b.ScrollItemPattern.ScrollIntoView()
        Sleep(600)
        b.Click("left")
        Sleep(3500)
        MerWaitNotHung(60)
        mainHwnd := WinExist(BRAVO_WIN_TITLE)
        for hwnd in WinGetList("ahk_exe Bravo.exe") {
            if (hwnd = mainHwnd || !DllCall("IsWindowVisible", "ptr", hwnd, "int"))
                continue
            wt := ""
            try wt := WinGetTitle(hwnd)
            out .= "## extra window title=" . wt . "`r`n"
            DUMP_COUNT := 0
            try MerDump(UIA.ElementFromHandle(hwnd), 0, &out)
        }
        out .= "## main window`r`n"
        DUMP_COUNT := 0
        try MerDump(GetBravoRoot(), 0, &out)
        MerShot(st . "_tpl_" . slug)
    }
    MerWrite(OUT_DIR . "\" . st . "_tpl_" . slug . ".txt", out)
    MerCancelAll(st)
    ok := false
    try ok := BackToDashboard()
    if !ok {
        MerStatus("ABORT no-dashboard-after " . st . " " . bname)
        ExitApp(4)
    }
    return true
}

MerDump(el, depth, &out) {
    global DUMP_COUNT
    if (depth > 30 || DUMP_COUNT > 9000)
        return
    DUMP_COUNT += 1
    t := "", n := "", c := "", rs := "", v := "", tg := "", tx := ""
    try t := el.LocalizedType
    try n := el.Name
    try c := el.ClassName
    try {
        r := el.BoundingRectangle
        rs := r.l . "," . r.t . "," . r.r . "," . r.b
    }
    try v := el.Value
    if (c = "CheckBox") {
        try tg := String(el.ToggleState)
    }
    if (c = "RichTextBox" || t = "document") {
        try tx := el.TextPattern.DocumentRange.GetText(-1)
    }
    ind := ""
    Loop depth
        ind .= "  "
    line := ind . "[" . t . "] N=" . MerClean(n, 400) . " | C=" . MerClean(c, 80) . " | R=" . rs
    if (tg != "")
        line .= " | TOGGLE=" . tg
    if (v != "")
        line .= " | V=" . MerClean(v, 400)
    if (tx != "")
        line .= " | TEXT=" . MerClean(tx, 1200)
    out .= line . "`r`n"
    kids := []
    try kids := el.GetChildren()
    for k in kids
        MerDump(k, depth + 1, &out)
}

MerPipelineBusy() {
    Loop Files, A_ScriptDir . "\triggers\*.json" {
        if (DateDiff(A_Now, A_LoopFileTimeModified, "Minutes") < 30)
            return "pending " . A_LoopFileName
    }
    Loop Files, A_ScriptDir . "\triggers\claimed\*.json" {
        if (DateDiff(A_Now, A_LoopFileTimeModified, "Seconds") < 180)
            return "claimed " . A_LoopFileName
    }
    return ""
}

MerFind(root, cond) {
    el := 0
    try el := root.FindElement(cond)
    return el
}

MerWaitNotHung(sec) {
    t0 := A_TickCount
    Loop {
        h := WinExist(BRAVO_WIN_TITLE)
        if !h || !DllCall("IsHungAppWindow", "ptr", h, "int")
            return true
        if (A_TickCount - t0 > sec * 1000)
            return false
        Sleep(3000)
    }
}

MerShot(key) {
    pngEsc := StrReplace(OUT_DIR . "\" . key . ".png", "'", "''")
    cmd := "powershell -NoProfile -WindowStyle Hidden -Command `"Add-Type -AssemblyName System.Windows.Forms; Add-Type -AssemblyName System.Drawing; $b = New-Object System.Drawing.Bitmap([System.Windows.Forms.SystemInformation]::VirtualScreen.Width, [System.Windows.Forms.SystemInformation]::VirtualScreen.Height); $g = [System.Drawing.Graphics]::FromImage($b); $g.CopyFromScreen([System.Windows.Forms.SystemInformation]::VirtualScreen.Location, [System.Drawing.Point]::Empty, $b.Size); $b.Save('" . pngEsc . "', 'Png'); $g.Dispose(); $b.Dispose()`""
    try RunWait(cmd, , "Hide")
}

MerClean(s, n) {
    s := String(s)
    s := StrReplace(s, "`r", " ")
    s := StrReplace(s, "`n", " ")
    s := StrReplace(s, "`t", " ")
    s := StrReplace(s, "|", "/")
    return SubStr(s, 1, n)
}

MerWrite(path, text) {
    try FileDelete(path)
    FileAppend(text, path, "UTF-8-RAW")
}

MerStatus(s) {
    try FileDelete(STATUS_FILE)
    try FileAppend(FormatTime(, "yyyy-MM-dd HH:mm:ss") . " " . s, STATUS_FILE, "UTF-8-RAW")
    try LogMessage("status: " . s)
}

MerOnError(e, mode) {
    try LogMessage("UNHANDLED: " . e.Message . " line " . e.Line)
    try MerStatus("ABORT unhandled " . e.Message)
    ExitApp(3)
    return 1
}
