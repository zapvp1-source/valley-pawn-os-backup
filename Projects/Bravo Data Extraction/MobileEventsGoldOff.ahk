; ============================================================================
; MobileEventsGoldOff.ahk -- STANDALONE (added 2026-11-19, Joshua: "change it and make sure they are all off at all stores").
; Per store: opens Customers > Schedule Mobile Event, and for every event whose TITLE box contains "gold"
; (We Buy Gold / one-time Gold), clears its enabled checkbox if it is on. Nothing else is touched.
; If something was changed it presses the editor's "Ok"; if nothing needed changing it leaves by "Cancel".
; Then re-opens the editor, writes what it shows to output\mobile_events\<STORE>.txt and leaves by Cancel.
; Mode "channels" (WAY only): opens the first event's channel drop-down, records the choices, closes it, Cancel.
; Writes a per-store line to output\mobile_events\_goldoff.txt. ASCII only.
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
global RESULT_FILE := OUT_DIR . "\_goldoff.txt"
global STORES      := StrSplit((A_Args.Length >= 1) ? A_Args[1] : "WAY", ",")
global MODE        := (A_Args.Length >= 2) ? A_Args[2] : "off"
global EDITOR_TEXT := "The enabled events below are scheduled to send a message to all mobile customers"
global DUMP_COUNT  := 0
OnError(MerOnError)
GoMain()
ExitApp(0)

GoMain() {
    global
    if !DirExist(OUT_DIR)
        DirCreate(OUT_DIR)
    InitLog(A_ScriptDir . "\logs", "mobileevents-goldoff-" . FormatTime(, "yyyy-MM-ddTHH-mm-ss"))
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
            GoResult(st, "SKIP could not reach store")
            continue
        }
        Sleep(1500)
        DismissPopups()
        if (GetCurrentStoreCode() != st) {
            GoResult(st, "SKIP title bar not " . st)
            continue
        }
        if (MODE = "channels")
            GoChannels(st)
        else if (MODE = "probe")
            GoProbe(st)
        else if (MODE = "align") {
            GoAlign(st)
            GoVerify(st)
        }
        else {
            GoOff(st)
            GoVerify(st)
        }
        done .= st . " "
    }
    try BackToDashboard()
    MerStatus("COMPLETE done=" . done)
}

; returns [checkbox, title] pairs for every event row in the editor list
GoRows() {
    pane := MerFind(GetBravoRoot(), {ClassName: "ScrollViewer"})
    rows := []
    if !pane
        return rows
    cb := 0
    for k in pane.GetChildren() {
        c := ""
        try c := k.ClassName
        if (c = "CheckBox") {
            cb := k
            continue
        }
        if (cb && c = "BravoMaskedTextBox") {
            v := ""
            try v := k.Value
            rows.Push([cb, v])
            cb := 0
        } else if (cb && c = "TextBlock") {
            n := ""
            try n := k.Name
            rows.Push([cb, n])
            cb := 0
        }
    }
    return rows
}

GoOff(st) {
    if !MerOpenEditor() {
        GoResult(st, "ERROR editor did not open")
        try BackToDashboard()
        return
    }
    rows := GoRows()
    changed := 0, seen := 0, already := 0
    for r in rows {
        if !InStr(r[2], "gold")
            continue
        seen += 1
        ts := -1
        try ts := r[1].ToggleState
        if (ts = 1) {
            r[1].TogglePattern.Toggle()
            Sleep(800)
            ts2 := -1
            try ts2 := r[1].ToggleState
            if (ts2 = 0)
                changed += 1
            else
                LogMessage("toggle did not clear for " . r[2])
        } else
            already += 1
    }
    line := "rows=" . rows.Length . " gold=" . seen . " turned_off=" . changed . " already_off=" . already
    if (changed > 0) {
        okt := MerFind(GetBravoRoot(), {Name: "Ok", Type: "Text"})
        if !okt {
            GoResult(st, "ERROR Ok not found, leaving by Cancel " . line)
            MerCancelAll(st)
            try BackToDashboard()
            return
        }
        okt.Click("left")
        Sleep(4000)
        MerWaitNotHung(90)
        ; any extra dialog after Ok is recorded, then closed by Cancel only
        mainHwnd := WinExist(BRAVO_WIN_TITLE)
        for hwnd in WinGetList("ahk_exe Bravo.exe") {
            if (hwnd = mainHwnd || !DllCall("IsWindowVisible", "ptr", hwnd, "int"))
                continue
            out := ""
            DUMP_COUNT := 0
            try MerDump(UIA.ElementFromHandle(hwnd), 0, &out)
            MerWrite(OUT_DIR . "\" . st . "_after_ok_dialog.txt", out)
            line .= " DIALOG-after-ok"
        }
        if ExistsByName(EDITOR_TEXT) {
            line .= " editor-still-open"
            MerCancelAll(st)
        } else
            line .= " saved"
    } else
        MerCancelAll(st)
    GoResult(st, line)
    try BackToDashboard()
}

GoVerify(st) {
    if !MerOpenEditor() {
        GoResult(st, "VERIFY editor did not open")
        try BackToDashboard()
        return
    }
    title := ""
    try title := WinGetTitle(BRAVO_WIN_TITLE)
    out := "# store: " . st . "`r`n# captured: " . FormatTime(, "yyyy-MM-dd HH:mm:ss") . "`r`n# title: " . title . "`r`n# editor_open: yes`r`n"
    out .= "# format: [type] N=name | C=class | R=l,t,r,b | TOGGLE=0/1 | V=value | TEXT=document text`r`n"
    DUMP_COUNT := 0
    try MerDump(GetBravoRoot(), 0, &out)
    MerWrite(OUT_DIR . "\" . st . ".txt", out)
    on := 0
    for r in GoRows()
        if (InStr(r[2], "gold") && r[1].ToggleState = 1)
            on += 1
    GoResult(st, "VERIFY gold_events_still_on=" . on)
    MerCancelAll(st)
    try BackToDashboard()
}

GoChannels(st) {
    if !MerOpenEditor() {
        GoResult(st, "CHANNELS editor did not open")
        try BackToDashboard()
        return
    }
    out := ""
    combos := []
    try combos := MerFind(GetBravoRoot(), {ClassName: "ScrollViewer"}).FindElements({ClassName: "BravoComboBox"})
    if (combos.Length > 0) {
        c := combos[1]
        try {
            c.ExpandCollapsePattern.Expand()
            Sleep(2000)
            mainHwnd := WinExist(BRAVO_WIN_TITLE)
            for hwnd in WinGetList("ahk_exe Bravo.exe") {
                if (hwnd = mainHwnd || !DllCall("IsWindowVisible", "ptr", hwnd, "int"))
                    continue
                out .= "## popup`r`n"
                DUMP_COUNT := 0
                try MerDump(UIA.ElementFromHandle(hwnd), 0, &out)
            }
            out .= "## combo subtree`r`n"
            DUMP_COUNT := 0
            try MerDump(c, 0, &out)
            try c.ExpandCollapsePattern.Collapse()
            Sleep(1000)
        } catch as e {
            out .= "# error " . e.Message . "`r`n"
            try c.ExpandCollapsePattern.Collapse()
        }
    } else
        out .= "# no combo found`r`n"
    MerWrite(OUT_DIR . "\" . st . "_channels.txt", out)
    GoResult(st, "CHANNELS read, leaving by Cancel")
    MerCancelAll(st)
    try BackToDashboard()
}

; probe (2026-11-19): READ ONLY. Opens the first event's delivery drop-down with its arrow button, records every
; window, closes it with Escape; then clicks "Add new event", records the screen, and leaves by Cancel (nothing saved).
GoProbe(st) {
    global DUMP_COUNT
    if !MerOpenEditor() {
        GoResult(st, "PROBE editor did not open")
        try BackToDashboard()
        return
    }
    out := ""
    pane := MerFind(GetBravoRoot(), {ClassName: "ScrollViewer"})
    combo := 0
    for k in pane.GetChildren() {
        c := ""
        try c := k.ClassName
        if (c = "BravoComboBox") {
            combo := k
            break
        }
    }
    if combo {
        arrow := 0
        try arrow := combo.FindElement({Type: "Button"})
        if arrow {
            arrow.Click("left")
            Sleep(2500)
            mainHwnd := WinExist(BRAVO_WIN_TITLE)
            for hwnd in WinGetList("ahk_exe Bravo.exe") {
                if (hwnd = mainHwnd || !DllCall("IsWindowVisible", "ptr", hwnd, "int"))
                    continue
                out .= "## popup window`r`n"
                DUMP_COUNT := 0
                try MerDump(UIA.ElementFromHandle(hwnd), 0, &out)
            }
            out .= "## combo subtree`r`n"
            DUMP_COUNT := 0
            try MerDump(combo, 0, &out)
            MerShot(st . "_probe_combo")
            Send("{Escape}")
            Sleep(1500)
        } else
            out .= "# no arrow button`r`n"
    } else
        out .= "# no combo`r`n"
    MerWrite(OUT_DIR . "\" . st . "_probe_combo.txt", out)
    ; still open? (Escape could close the editor) -> reopen
    if !ExistsByName(EDITOR_TEXT) {
        try BackToDashboard()
        if !MerOpenEditor() {
            GoResult(st, "PROBE combo read; editor gone before add-event")
            return
        }
    }
    out := ""
    add := MerFind(GetBravoRoot(), {Name: "Add new event", Type: "Text"})
    if add {
        add.Click("left")
        Sleep(3000)
        mainHwnd := WinExist(BRAVO_WIN_TITLE)
        for hwnd in WinGetList("ahk_exe Bravo.exe") {
            if (hwnd = mainHwnd || !DllCall("IsWindowVisible", "ptr", hwnd, "int"))
                continue
            out .= "## popup window`r`n"
            DUMP_COUNT := 0
            try MerDump(UIA.ElementFromHandle(hwnd), 0, &out)
        }
        out .= "## editor list after add`r`n"
        DUMP_COUNT := 0
        try MerDump(MerFind(GetBravoRoot(), {ClassName: "ScrollViewer"}), 0, &out)
        MerShot(st . "_probe_add")
    } else
        out .= "# Add new event not found`r`n"
    MerWrite(OUT_DIR . "\" . st . "_probe_add.txt", out)
    GoResult(st, "PROBE done, leaving by Cancel (nothing saved)")
    MerCancelAll(st)
    try BackToDashboard()
}

; align (2026-11-19, Joshua: "make these all consistent across all 5"):
;  - any of the five standard events (Birthday, Store Anniversary, Loan Courtesy Reminder, Layaway Notice,
;    Loan Past Due (Due Date)) set to SMS is switched to AUTO (what the other stores use), via the drop-down list;
;  - the Birthday wording "15% OFF the in the next 30 days!" is corrected to "15% OFF during the next 30 days."
; Everything is checked in the editor before Ok; if any check fails it leaves by Cancel (nothing saved).
GoAlign(st) {
    global DUMP_COUNT
    if !MerOpenEditor() {
        GoResult(st, "ALIGN editor did not open")
        try BackToDashboard()
        return
    }
    pane := MerFind(GetBravoRoot(), {ClassName: "ScrollViewer"})
    std := Map("Birthday",1, "Store Anniversary",1, "Loan Courtesy Reminder",1, "Layaway Notice",1, "Loan Past Due (Due Date)",1)
    title := "", changed := 0, failed := 0, log := ""
    for k in pane.GetChildren() {
        c := "", n := "", v := ""
        try c := k.ClassName
        if (c = "CheckBox") {
            title := ""
            continue
        }
        if (title = "" && c = "TextBlock") {
            try n := k.Name
            title := n
            continue
        }
        if (title = "" && c = "BravoMaskedTextBox") {
            title := "(custom)"
            continue
        }
        if (c = "BravoComboBox" && std.Has(title)) {
            try v := k.Value
            if (v = "NTFSMS") {
                ok := false
                Loop 3 {
                    GoBringIntoView(pane, k)
                    Sleep(1000)
                    ok := GoPick(k, "AUTO")
                    v2 := ""
                    try v2 := k.Value
                    if (ok && v2 = "NTFAUT")
                        break
                    Sleep(1500)
                }
                v2 := ""
                try v2 := k.Value
                if (ok && v2 = "NTFAUT") {
                    changed += 1
                    log .= " " . title . ":SMS->AUTO"
                } else {
                    failed += 1
                    log .= " " . title . ":FAILED(" . v2 . ")"
                }
            }
        }
        if (c = "RichTextBox" && title = "Birthday") {
            tp := 0
            try tp := k.TextPattern
            if tp {
                txt := tp.DocumentRange.GetText(-1)
                if InStr(txt, "the in the next 30 days!", true) {
                    r := tp.DocumentRange.FindText("the in the next 30 days!")
                    if r {
                        r.Select()
                        k.SetFocus()
                        Sleep(500)
                        sel := ""
                        try sel := tp.GetSelection()[1].GetText(-1)
                        if (sel = "the in the next 30 days!") {
                            SendText("during the next 30 days.")
                            Sleep(1200)
                            t2 := tp.DocumentRange.GetText(-1)
                            if (InStr(t2, "15% OFF during the next 30 days.", true) && !InStr(t2, "the in the", true)) {
                                changed += 1
                                log .= " Birthday:typo-fixed"
                            } else {
                                failed += 1
                                log .= " Birthday:typo-check-failed[" . MerClean(t2, 200) . "]"
                            }
                        } else {
                            failed += 1
                            log .= " Birthday:select-failed[" . MerClean(sel, 80) . "]"
                        }
                    }
                }
            }
        }
    }
    line := "ALIGN changed=" . changed . " failed=" . failed . log
    if (changed > 0 && failed = 0) {
        okt := MerFind(GetBravoRoot(), {Name: "Ok", Type: "Text"})
        if !okt {
            GoResult(st, line . " | Ok not found, Cancel")
            MerCancelAll(st)
            try BackToDashboard()
            return
        }
        okt.Click("left")
        Sleep(4000)
        MerWaitNotHung(90)
        if ExistsByName(EDITOR_TEXT) {
            line .= " | editor-still-open, Cancel"
            MerCancelAll(st)
        } else
            line .= " | saved"
    } else {
        line .= " | nothing saved"
        MerCancelAll(st)
    }
    GoResult(st, line)
    try BackToDashboard()
}

; scrolls the editor list until el is fully inside the visible part of the list
GoBringIntoView(pane, el) {
    Loop 40 {
        pr := pane.BoundingRectangle, r := el.BoundingRectangle
        if (r.t >= pr.t + 5 && r.b <= pr.b - 5)
            return true
        try pane.ScrollPattern.Scroll((r.t < pr.t + 5) ? 1 : 4, 2)
        catch
            return false
        Sleep(250)
    }
    return false
}

; opens a BravoComboBox list with its arrow button (Invoke, no mouse) and selects the item whose text is want
GoPick(combo, want) {
    arrow := 0
    try arrow := combo.FindElement({Type: "Button"})
    if !arrow
        return false
    try arrow.InvokePattern.Invoke()
    catch {
        try arrow.ScrollItemPattern.ScrollIntoView()
        Sleep(500)
        arrow.Click("left")
    }
    Sleep(2500)
    mainHwnd := WinExist(BRAVO_WIN_TITLE)
    for hwnd in WinGetList("ahk_exe Bravo.exe") {
        if (hwnd = mainHwnd || !DllCall("IsWindowVisible", "ptr", hwnd, "int"))
            continue
        lst := 0
        try lst := UIA.ElementFromHandle(hwnd).FindElement({ClassName: "ListBox"})
        if !lst
            continue
        for it in lst.GetChildren() {
            t := 0
            try t := it.FindElement({Type: "Text"})
            if (t && t.Name = want) {
                try it.SelectionItemPattern.Select()
                catch
                    it.Click("left")
                Sleep(1000)
                ; make sure the list is closed
                still := false
                for h2 in WinGetList("ahk_exe Bravo.exe")
                    if (h2 = hwnd && DllCall("IsWindowVisible", "ptr", h2, "int"))
                        still := true
                if still {
                    try it.Click("left")
                    Sleep(800)
                }
                return true
            }
        }
    }
    Send("{Escape}")
    Sleep(800)
    return false
}

GoResult(st, s) {
    try FileAppend(FormatTime(, "yyyy-MM-dd HH:mm:ss") . " " . st . " " . s . "`r`n", RESULT_FILE, "UTF-8-RAW")
    try LogMessage("result " . st . ": " . s)
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
