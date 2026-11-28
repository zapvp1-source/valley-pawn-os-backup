; ============================================================================
; InvReportBuild.ahk -- STANDALONE (eBay Desk, 2026-11-21, Joshua approved: clone of MobileEventsGoldOff.ahk for Inventory > Custom Reports).
; Mode "invprobe" is READ ONLY. Original header follows.
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
global OUT_DIR     := A_ScriptDir . "\output\inv_reports"
global STATUS_FILE := OUT_DIR . "\_status.txt"
global RESULT_FILE := OUT_DIR . "\_results.txt"
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
    InitLog(A_ScriptDir . "\logs", "invreport-" . FormatTime(, "yyyy-MM-ddTHH-mm-ss"))
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
        if (MODE = "invprobe")
            GoInvProbe(st)
        else if (MODE = "layprobe")
            GoLayProbe(st)
        else if (MODE = "layprobe2")
            GoLayProbe2(st)
        else if (MODE = "layprobe3")
            GoLayProbe3(st)
        else if (MODE = "itemdry")
            GoItemBuild(st, false)
        else if (MODE = "itembuild")
            GoItemBuild(st, true)
        else if (MODE = "laydry")
            GoLayBuild(st, false)
        else if (MODE = "laybuild")
            GoLayBuild(st, true)
        else if (MODE = "stockdry")
            GoInvBuild(st, false, "C")
        else if (MODE = "stockbuild")
            GoInvBuild(st, true, "C")
        else if (MODE = "invdry")
            GoInvBuildAll(st, false)
        else if (MODE = "invbuild")
            GoInvBuildAll(st, true)
        else if (MODE = "channels")
            GoChannels(st)
        else if (MODE = "probe")
            GoProbe(st)
        else if (MODE = "crprobe")
            GoCrProbe(st)
        else if (MODE = "crdry")
            GoCrBuild(st, false)
        else if (MODE = "crbuild")
            GoCrBuild(st, true)
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

; crprobe (2026-11-20): READ ONLY. Loans/Buys > Custom Reports: dump the dialog, press "New Report", dump again,
; open the criteria drop-down and dump its list, close it with Escape, then leave by Cancel. Never Save / Delete Report.
GoCrProbe(st) {
    global DUMP_COUNT
    el := MerFind(GetBravoRoot(), {Name: "Loans/Buys"})
    if !el {
        GoResult(st, "CRPROBE Loans/Buys not found")
        return
    }
    el.Click("left")
    Sleep(5000)
    DismissPopups()
    MerWaitNotHung(90)
    cr := MerFind(GetBravoRoot(), {Name: "Custom Reports", Type: "Button"})
    if !cr {
        GoResult(st, "CRPROBE Custom Reports button not found")
        try BackToDashboard()
        return
    }
    cr.Click("left")
    Sleep(4000)
    MerWaitNotHung(60)
    if !MerFind(GetBravoRoot(), {AutomationId: "BoxSelectCriteria"}) {
        GoResult(st, "CRPROBE dialog did not open")
        try BackToDashboard()
        return
    }
    out := "## dialog as opened`r`n"
    DUMP_COUNT := 0
    try MerDump(GetBravoRoot(), 0, &out)
    MerShot(st . "_crprobe_1")
    nr := MerFind(GetBravoRoot(), {Name: "New Report", Type: "Button"})
    if nr {
        nr.Click("left")
        Sleep(2500)
        out .= "## after New Report`r`n"
        DUMP_COUNT := 0
        try MerDump(GetBravoRoot(), 0, &out)
        MerShot(st . "_crprobe_2")
    } else
        out .= "## New Report button not found`r`n"
    for aid in ["BoxSelectCriteria", "BoxIsShared", "BoxColumns"] {
        cb := MerFind(GetBravoRoot(), {AutomationId: aid})
        if !cb
            continue
        arrow := 0
        try arrow := cb.FindElement({Type: "Button"})
        if !arrow
            continue
        try arrow.InvokePattern.Invoke()
        catch
            arrow.Click("left")
        Sleep(2000)
        out .= "## list of " . aid . "`r`n"
        mainHwnd := WinExist(BRAVO_WIN_TITLE)
        for hwnd in WinGetList("ahk_exe Bravo.exe") {
            if (hwnd = mainHwnd || !DllCall("IsWindowVisible", "ptr", hwnd, "int"))
                continue
            DUMP_COUNT := 0
            try MerDump(UIA.ElementFromHandle(hwnd), 0, &out)
        }
        Send("{Escape}")
        Sleep(1200)
    }
    MerWrite(OUT_DIR . "\" . st . "_crprobe.txt", out)
    closed := false
    Loop 5 {
        if !MerFind(GetBravoRoot(), {AutomationId: "BoxSelectCriteria"}) {
            closed := true
            break
        }
        c := MerFind(GetBravoRoot(), {Name: "Cancel", Type: "Button"})
        if c
            c.Click("left")
        Sleep(2500)
    }
    GoResult(st, "CRPROBE done, dialog " . (closed ? "closed by Cancel" : "STILL OPEN") . " (nothing saved)")
    try BackToDashboard()
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

; ============================================================================
; crdry / crbuild (2026-11-20, Joshua "yes" to ONE new saved report). Loans/Buys > Custom Reports > New Report:
; name "Claude Loan Reminders", Shared Company-Wide, layout FDP, Ticket Kind = LOAN, Due Date range (two dates).
; ADDITIVE ONLY: never loads, updates or deletes an existing saved report. crdry does everything except Save and
; leaves by Cancel. crbuild presses the form's own Save only if every check passes; otherwise Cancel.
; ============================================================================
CrPopups() {
    res := []
    mainHwnd := WinExist(BRAVO_WIN_TITLE)
    for hwnd in WinGetList("ahk_exe Bravo.exe") {
        if (hwnd = mainHwnd || !DllCall("IsWindowVisible", "ptr", hwnd, "int"))
            continue
        el := 0
        try el := UIA.ElementFromHandle(hwnd)
        if !el
            continue
        c := ""
        try c := el.ClassName
        if (c = "Popup")
            res.Push(el)
    }
    return res
}

CrDumpPopups(&out, label) {
    global DUMP_COUNT
    out .= "## popups: " . label . "`r`n"
    for p in CrPopups() {
        DUMP_COUNT := 0
        try MerDump(p, 0, &out)
    }
}

; opens a combo's list, scans it (scrolling) for one of wants; selects it when doSelect. Returns the matched text or "".
CrPick(combo, wants, &seen, doSelect := true, byClick := false) {
    arrow := 0
    try arrow := combo.FindElement({Type: "Button"})
    if !arrow
        return ""
    try arrow.InvokePattern.Invoke()
    catch
        arrow.Click("left")
    Sleep(2200)
    pops := CrPopups()
    if (pops.Length = 0)
        return ""
    lst := 0
    try lst := pops[1].FindElement({ClassName: "ListBox"})
    if !lst {
        Send("{Escape}")
        Sleep(900)
        return ""
    }
    found := 0, foundName := "", v := 0
    Loop 12 {
        kids := []
        try kids := lst.GetChildren()
        for it in kids {
            txts := []
            try txts := it.FindElements({Type: "Text"})
            for t in txts {
                n := ""
                try n := t.Name
                if (n = "")
                    continue
                if !InStr(seen, ";" . n . ";")
                    seen .= n . ";"
                for w in wants
                    if (n = w)
                        found := it, foundName := n
            }
            if found
                break
        }
        if (found || v >= 100)
            break
        v += 10
        try lst.ScrollPattern.SetScrollPercent(v)
        catch
            break
        Sleep(450)
    }
    if (!found || !doSelect) {
        if (CrPopups().Length > 0) {
            Send("{Escape}")
            Sleep(900)
        }
        return doSelect ? "" : foundName
    }
    try found.ScrollItemPattern.ScrollIntoView()
    Sleep(400)
    ok := false
    if !byClick {
        try {
            found.SelectionItemPattern.Select()
            ok := true
        }
    }
    if !ok
        try found.Click("left")
    Sleep(1300)
    if (CrPopups().Length > 0) {
        Send("{Enter}")
        Sleep(1300)
    }
    if (CrPopups().Length > 0) {
        Send("{Escape}")
        Sleep(900)
    }
    return foundName
}

; text of the selected item in a combo's list (opens it, reads, Escape)
CrSelected(combo) {
    arrow := 0
    try arrow := combo.FindElement({Type: "Button"})
    if !arrow
        return ""
    try arrow.InvokePattern.Invoke()
    catch
        arrow.Click("left")
    Sleep(2000)
    sel := ""
    global CR_DBG
    CR_DBG .= "[sel-read pops=" . CrPopups().Length . "]"
    for p in CrPopups() {
        its := []
        try its := p.FindElements({Type: "ListItem"})
        for it in its {
            s := false, tn := ""
            try s := it.SelectionItemPattern.IsSelected
            try tn := it.FindElement({Type: "Text"}).Name
            CR_DBG .= " " . tn . "=" . s
            if (s && sel = "")
                sel := tn
        }
    }
    if (CrPopups().Length > 0) {
        Send("{Escape}")
        Sleep(900)
    }
    return sel
}

CrList() {
    return MerFind(GetBravoRoot(), {ClassName: "FilterEditingCriteriaListView"})
}

; names of the Text children of the criteria list, in order, joined by " | "
CrRowTexts() {
    s := ""
    lv := CrList()
    if !lv
        return s
    for k in lv.GetChildren() {
        c := "", n := ""
        try c := k.ClassName
        try n := k.Name
        if (c = "TextBlock" && n != "")
            s .= n . " | "
    }
    return s
}

; first child of the criteria list with class cls that comes after the Text child named label (same row)
CrAfter(label, cls) {
    lv := CrList()
    if !lv
        return 0
    hit := false
    for k in lv.GetChildren() {
        c := "", n := ""
        try c := k.ClassName
        try n := k.Name
        if (!hit) {
            if (c = "TextBlock" && n = label)
                hit := true
            continue
        }
        if (c = "Button")
            return 0
        if (c = cls)
            return k
    }
    return 0
}

CrDateEdits() {
    res := []
    lv := CrList()
    if !lv
        return res
    for k in lv.GetChildren() {
        c := ""
        try c := k.ClassName
        if (c = "BravoDateEdit")
            res.Push(k)
    }
    return res
}

CrCancelOut(&out) {
    global DUMP_COUNT
    closed := false
    Loop 5 {
        if !MerFind(GetBravoRoot(), {AutomationId: "BoxSelectCriteria"}) {
            closed := true
            break
        }
        if (CrPopups().Length > 0) {
            Send("{Escape}")
            Sleep(900)
        }
        c := MerFind(GetBravoRoot(), {Name: "Cancel", Type: "Button"})
        if c
            c.Click("left")
        Sleep(2500)
        if (A_Index = 2) {
            out .= "## still open after 2 cancels`r`n"
            DUMP_COUNT := 0
            try MerDump(GetBravoRoot(), 0, &out)
        }
    }
    return closed
}

GoCrBuild(st, doSave) {
    global DUMP_COUNT, CR_NAME, CR_DBG
    CR_DBG := ""
    CR_NAME := "Claude Loan Reminders"
    tag := doSave ? "CRBUILD" : "CRDRY"
    out := ""
    outFile := OUT_DIR . "\" . st . "_" . StrLower(tag) . ".txt"
    el := MerFind(GetBravoRoot(), {Name: "Loans/Buys"})
    if !el {
        GoResult(st, tag . " Loans/Buys not found")
        return
    }
    el.Click("left")
    Sleep(5000)
    DismissPopups()
    MerWaitNotHung(90)
    cr := MerFind(GetBravoRoot(), {Name: "Custom Reports", Type: "Button"})
    if !cr {
        GoResult(st, tag . " Custom Reports button not found")
        try BackToDashboard()
        return
    }
    cr.Click("left")
    Sleep(4000)
    MerWaitNotHung(60)
    if !MerFind(GetBravoRoot(), {AutomationId: "BoxSelectCriteria"}) {
        GoResult(st, tag . " dialog did not open")
        try BackToDashboard()
        return
    }
    verdict := ""
    saved := false
    try {
        ; a. does the report already exist?
        bar := MerFind(GetBravoRoot(), {ClassName: "EntityAdvancedSearchControlBarView"})
        sc := bar ? MerFind(bar, {ClassName: "BravoComboBox"}) : 0
        if !sc
            throw Error("saved-report list not found")
        seen := ";"
        have := ""
        Loop 3 {
            have := CrPick(sc, [CR_NAME], &seen, false)
            if (have != "" || StrLen(seen) >= 20)
                break
            Sleep(2000)
        }
        out .= "## saved reports seen: " . seen . "`r`n"
        if (have != "")
            throw Error("ALREADY EXISTS - nothing to do")
        if (StrLen(seen) < 20)
            throw Error("saved-report list could not be read")
        ; b. New Report
        nr := MerFind(GetBravoRoot(), {Name: "New Report", Type: "Button"})
        if !nr
            throw Error("New Report button not found")
        nr.Click("left")
        Sleep(2500)
        nb := MerFind(GetBravoRoot(), {AutomationId: "BoxReportName"})
        if !nb
            throw Error("report name box not found")
        v := ""
        try v := nb.Value
        if (v != "" || CrRowTexts() != "")
            throw Error("form not blank after New Report (name='" . v . "' rows='" . CrRowTexts() . "')")
        if MerFind(GetBravoRoot(), {Name: "Update", Type: "Button"})
            throw Error("Update button present - an existing report is loaded")
        ; c. name
        inner := MerFind(nb, {ClassName: "TextBox"})
        (inner ? inner : nb).Click("left")
        Sleep(500)
        Send("^a")
        Sleep(200)
        SendText(CR_NAME)
        Sleep(500)
        Send("{Tab}")
        Sleep(900)
        v := ""
        try v := MerFind(GetBravoRoot(), {AutomationId: "BoxReportName"}).Value
        nameOk := (v = CR_NAME)
        out .= "name box = '" . v . "'`r`n"
        ; d. shared company-wide
        s1 := ";"
        CR_DBG := ""
        before := CrSelected(MerFind(GetBravoRoot(), {AutomationId: "BoxIsShared"}))
        pk := CrPick(MerFind(GetBravoRoot(), {AutomationId: "BoxIsShared"}), ["Shared Company-Wide"], &s1, true, true)
        shSel := CrSelected(MerFind(GetBravoRoot(), {AutomationId: "BoxIsShared"}))
        out .= "shared before='" . before . "' pick returned '" . pk . "' seen " . s1 . " dbg " . CR_DBG . "`r`n"
        sharedOk := (shSel = "Shared Company-Wide")
        out .= "shared selected = '" . shSel . "'`r`n"
        ; e. layout FDP
        s2 := ";"
        CrPick(MerFind(GetBravoRoot(), {AutomationId: "BoxColumns"}), ["FDP"], &s2)
        v := ""
        try v := MerFind(GetBravoRoot(), {AutomationId: "BoxColumns"}).Value
        layoutOk := InStr(v, "66b3ae3b") > 0
        out .= "layout value = '" . v . "'`r`n"
        ; f. Ticket Kind = LOAN
        s3 := ";"
        CrPick(MerFind(GetBravoRoot(), {AutomationId: "BoxSelectCriteria"}), ["Ticket Kind"], &s3)
        out .= "criteria seen: " . s3 . "`r`n"
        out .= "rows after Ticket Kind: " . CrRowTexts() . "`r`n"
        kc := CrAfter("Ticket Kind", "BravoComboBox")
        kindOk := false
        if kc {
            s4 := ";"
            CrPick(kc, ["LOAN", "Loan"], &s4)
            out .= "ticket kinds seen: " . s4 . "`r`n"
            v := ""
            try v := CrAfter("Ticket Kind", "BravoComboBox").Value
            out .= "ticket kind value = '" . v . "'`r`n"
            kindOk := InStr(v, "TKLOAN") > 0
        } else
            out .= "ticket kind value combo NOT found`r`n"
        ; g. Due Date range
        s5 := ";"
        CrPick(MerFind(GetBravoRoot(), {AutomationId: "BoxSelectCriteria"}), ["Due Date"], &s5)
        out .= "rows after Due Date: " . CrRowTexts() . "`r`n"
        if !InStr(CrRowTexts(), "Due Date | range") {
            lv := CrList()
            op := 0, hit := false
            for k in lv.GetChildren() {
                c := "", n := ""
                try c := k.ClassName
                try n := k.Name
                if (!hit) {
                    if (c = "TextBlock" && n = "Due Date")
                        hit := true
                    continue
                }
                if (c = "TextBlock") {
                    op := k
                    break
                }
            }
            if op {
                h := MerFind(op, {Type: "Hyperlink"})
                tgt := h ? h : op
                did := false
                try {
                    tgt.InvokePattern.Invoke()
                    did := true
                }
                if !did
                    tgt.Click("left")
                Sleep(1800)
                CrDumpPopups(&out, "operator list")
                rg := 0
                for p in CrPopups() {
                    try rg := p.FindElement({Name: "range", Type: "Text"})
                    if rg
                        break
                }
                if !rg
                    rg := MerFind(GetBravoRoot(), {Name: "range", Type: "Text"})
                if rg {
                    rg.Click("left")
                    Sleep(1300)
                }
                if (CrPopups().Length > 0 && !InStr(CrRowTexts(), "Due Date | range")) {
                    Send("{Enter}")
                    Sleep(1200)
                }
                if (CrPopups().Length > 0) {
                    Send("{Escape}")
                    Sleep(900)
                }
            } else
                out .= "operator text after Due Date NOT found`r`n"
        }
        rangeOk := InStr(CrRowTexts(), "Due Date | range") > 0
        d1 := FormatTime(DateAdd(A_Now, -10, "Days"), "M/d/yyyy")
        d2 := FormatTime(DateAdd(A_Now, 6, "Days"), "M/d/yyyy")
        ; type the dates like a person (setting the value directly leaves text, not a date, and Save rejects it)
        for i, dd in [d1, d2] {
            des := CrDateEdits()
            if (des.Length != 2)
                break
            tb := MerFind(des[i], {ClassName: "TextBox"})
            if !tb
                break
            tb.Click("left")
            Sleep(500)
            Send("^a")
            Sleep(200)
            SendText(dd)
            Sleep(400)
            Send("{Tab}")
            Sleep(700)
        }
        des := CrDateEdits()
        dv1 := "", dv2 := ""
        if (des.Length = 2) {
            try dv1 := des[1].Value
            try dv2 := des[2].Value
        }
        datesOk := (des.Length = 2 && RegExMatch(dv1, "^\d+/\d+/\d{4} 12:00:00 AM") && RegExMatch(dv2, "^\d+/\d+/\d{4} 12:00:00 AM"))  ; any real date: the runner overrides both at run time
        out .= "date edits = " . des.Length . " '" . dv1 . "' '" . dv2 . "' want " . d1 . " " . d2 . "`r`n"
        rows := CrRowTexts()
        out .= "final rows: " . rows . "`r`n"
        rowsOk := (rows = "Ticket Kind | = | LOAN | Due Date | range | " || rows = "Ticket Kind | = | Due Date | range | ")
        lay := MerFind(GetBravoRoot(), {ClassName: "LayoutView"})
        sb := lay ? MerFind(lay, {Name: "Save", Type: "Button"}) : 0
        noUpd := !MerFind(GetBravoRoot(), {Name: "Update", Type: "Button"})
        gate := "name=" . nameOk . " shared=" . sharedOk . " layout=" . layoutOk . " kind=" . kindOk . " range=" . rangeOk . " dates=" . datesOk . " rows=" . rowsOk . " save=" . (sb ? 1 : 0) . " noUpdate=" . noUpd
        out .= "GATE " . gate . "`r`n## form before save`r`n"
        DUMP_COUNT := 0
        try MerDump(GetBravoRoot().FindElement({ClassName: "LayoutView"}), 0, &out)
        DUMP_COUNT := 0
        try MerDump(GetBravoRoot().FindElement({ClassName: "FilterEditingView"}), 0, &out)
        MerShot(st . "_" . StrLower(tag) . "_1")
        allOk := (nameOk && sharedOk && layoutOk && kindOk && rangeOk && datesOk && rowsOk && sb && noUpd)
        if !allOk
            verdict := "NOSAVE " . gate
        else if !doSave
            verdict := "DRY OK (all checks pass, not saved) " . gate
        else {
            sb.Click("left")
            Sleep(4000)
            MerWaitNotHung(60)
            saved := true
            out .= "## after Save`r`n"
            CrDumpPopups(&out, "after save")
            MerShot(st . "_" . StrLower(tag) . "_2")
            if !MerFind(GetBravoRoot(), {AutomationId: "BoxSelectCriteria"}) {
                DismissPopups()
                cr2 := MerFind(GetBravoRoot(), {Name: "Custom Reports", Type: "Button"})
                if cr2 {
                    cr2.Click("left")
                    Sleep(4000)
                }
            }
            bar := MerFind(GetBravoRoot(), {ClassName: "EntityAdvancedSearchControlBarView"})
            sc := bar ? MerFind(bar, {ClassName: "BravoComboBox"}) : 0
            seen2 := ";"
            have := sc ? CrPick(sc, [CR_NAME], &seen2, false) : ""
            out .= "## saved reports after save: " . seen2 . "`r`n"
            verdict := (have != "") ? "SAVED+LISTED " . gate : "SAVE CLICKED but not seen in list " . gate
        }
    } catch as e {
        verdict := (saved ? "ERROR AFTER SAVE " : "NOSAVE ") . e.Message
    }
    closed := CrCancelOut(&out)
    MerShot(st . "_" . StrLower(tag) . "_end")
    MerWrite(outFile, out)
    GoResult(st, tag . " " . verdict . " / dialog " . (closed ? "closed" : "STILL OPEN"))
    try BackToDashboard()
}

; ============================================================================
; invprobe (2026-11-21, eBay Desk). READ ONLY. Inventory > Custom Reports:
; 1) dump dialog; 2) after New Report, record the choices in BoxSelectCriteria / BoxIsShared / BoxColumns;
; 3) Cancel, reopen, SELECT existing "Claude Sold Inv Details" and record its criteria + layout; Cancel.
; Never presses Save or Update.
; ============================================================================
GoInvOpen() {
    el := MerFind(GetBravoRoot(), {AutomationId: "Dashboard.Buttons.Inventory"})
    if !el
        el := MerFind(GetBravoRoot(), {Name: "Inventory"})
    if !el
        return false
    el.Click("left")
    Sleep(5000)
    DismissPopups()
    MerWaitNotHung(90)
    cr := MerFind(GetBravoRoot(), {Name: "Custom Reports", Type: "Button"})
    if !cr
        return false
    cr.Click("left")
    Sleep(4000)
    MerWaitNotHung(60)
    return MerFind(GetBravoRoot(), {AutomationId: "BoxSelectCriteria"}) ? true : false
}

GoInvProbe(st) {
    global DUMP_COUNT
    if !GoInvOpen() {
        GoResult(st, "INVPROBE dialog did not open")
        try BackToDashboard()
        return
    }
    out := "## dialog as opened`r`n"
    DUMP_COUNT := 0
    try MerDump(GetBravoRoot(), 0, &out)
    nr := MerFind(GetBravoRoot(), {Name: "New Report", Type: "Button"})
    if nr {
        nr.Click("left")
        Sleep(2500)
    } else
        out .= "## New Report button not found`r`n"
    for aid in ["BoxSelectCriteria", "BoxIsShared", "BoxColumns"] {
        cb := MerFind(GetBravoRoot(), {AutomationId: aid})
        if !cb
            continue
        seen := ";"
        CrPick(cb, ["__none__"], &seen, false)
        out .= "## list of " . aid . ": " . seen . "`r`n"
    }
    c1 := ""
    CrCancelOut(&c1)
    out .= c1
    try BackToDashboard()
    Sleep(2000)
    closed := false
    if GoInvOpen() {
        bar := MerFind(GetBravoRoot(), {ClassName: "EntityAdvancedSearchControlBarView"})
        sc := bar ? MerFind(bar, {ClassName: "BravoComboBox"}) : 0
        seen := ";"
        got := sc ? CrPick(sc, ["Claude Sold Inv Details"], &seen, true) : ""
        out .= "## saved reports: " . seen . "`r`n## selected '" . got . "'`r`n"
        Sleep(2500)
        v := ""
        try v := MerFind(GetBravoRoot(), {AutomationId: "BoxReportName"}).Value
        out .= "name box = '" . v . "'`r`nrows = " . CrRowTexts() . "`r`n"
        v := ""
        try v := MerFind(GetBravoRoot(), {AutomationId: "BoxColumns"}).Value
        out .= "layout value = '" . v . "'`r`n"
        out .= "layout selected = '" . CrSelected(MerFind(GetBravoRoot(), {AutomationId: "BoxColumns"})) . "'`r`n"
        out .= "shared selected = '" . CrSelected(MerFind(GetBravoRoot(), {AutomationId: "BoxIsShared"})) . "'`r`n## criteria list dump`r`n"
        DUMP_COUNT := 0
        try MerDump(CrList(), 0, &out)
        c2 := ""
        closed := CrCancelOut(&c2)
        out .= c2
    } else
        out .= "## reopen failed`r`n"
    MerWrite(OUT_DIR . "\" . st . "_invprobe.txt", out)
    GoResult(st, "INVPROBE done, dialog " . (closed ? "closed by Cancel" : "STILL OPEN") . " (nothing saved)")
    try BackToDashboard()
}


; ============================================================================
; invdry / invbuild (2026-11-21, eBay Desk, Joshua approved the two reports).
; Inventory > Custom Reports > New Report. ADDITIVE ONLY: never loads, updates or deletes an existing report.
;   A "Claude eBay Sold Today All": layout "Sold inv detail", Shared Company-Wide, Status = SOLD, Status Date range,
;      Store criterion added and EVERY store value selected when the value control allows it.
;   B "Claude eBay Listed": layout "Inv item detailed", Shared Company-Wide, Status = INVENTORY, Web Platform = eBay.
; invdry records every choice list and leaves by Cancel. invbuild presses Save only when every gate passes.
; ============================================================================
GoInvBuildAll(st, doSave) {
    GoInvBuild(st, doSave, "A")
    try BackToDashboard()
    Sleep(3000)
    GoInvBuild(st, doSave, "B")
}

GoInvCriteriaValues(label, &out) {
    vc := CrAfter(label, "BravoComboBox")
    if !vc {
        out .= label . " value control: no BravoComboBox in row; row classes:"
        lv := CrList(), hit := false
        for k in lv.GetChildren() {
            c := "", n := ""
            try c := k.ClassName
            try n := k.Name
            if (!hit) {
                if (c = "TextBlock" && n = label)
                    hit := true
                continue
            }
            if (c = "Button")
                break
            out .= " " . c . "(" . n . ")"
        }
        out .= "`r`n"
        return 0
    }
    seen := ";"
    CrPick(vc, ["__none__"], &seen, false)
    out .= label . " values: " . seen . "`r`n"
    return vc
}

GoInvBuild(st, doSave, which) {
    global DUMP_COUNT
    name := (which = "A") ? "Claude eBay Sold Today All" : ((which = "C") ? "Claude InStock Detail" : "Claude eBay Listed")
    layoutWant := (which = "A") ? "Sold inv detail" : ((which = "C") ? "Claude Item Master" : "Inv item detailed")
    tag := (doSave ? "INVBUILD" : "INVDRY") . which
    out := ""
    outFile := OUT_DIR . "\" . st . "_" . StrLower(tag) . ".txt"
    if !GoInvOpen() {
        GoResult(st, tag . " dialog did not open")
        try BackToDashboard()
        return
    }
    verdict := "", saved := false
    try {
        bar := MerFind(GetBravoRoot(), {ClassName: "EntityAdvancedSearchControlBarView"})
        sc := bar ? MerFind(bar, {ClassName: "BravoComboBox"}) : 0
        if !sc
            throw Error("saved-report list not found")
        seen := ";", have := ""
        Loop 3 {
            have := CrPick(sc, [name], &seen, false)
            if (have != "" || StrLen(seen) >= 20)
                break
            Sleep(2000)
        }
        if (have != "")
            throw Error("ALREADY EXISTS - nothing to do")
        if (StrLen(seen) < 20)
            throw Error("saved-report list could not be read")
        nr := MerFind(GetBravoRoot(), {Name: "New Report", Type: "Button"})
        if !nr
            throw Error("New Report button not found")
        nr.Click("left")
        Sleep(2500)
        nb := MerFind(GetBravoRoot(), {AutomationId: "BoxReportName"})
        if !nb
            throw Error("report name box not found")
        v := ""
        try v := nb.Value
        if (v != "" || CrRowTexts() != "")
            throw Error("form not blank after New Report")
        if MerFind(GetBravoRoot(), {Name: "Update", Type: "Button"})
            throw Error("Update button present - an existing report is loaded")
        inner := MerFind(nb, {ClassName: "TextBox"})
        (inner ? inner : nb).Click("left")
        Sleep(500)
        Send("^a")
        Sleep(200)
        SendText(name)
        Sleep(500)
        Send("{Tab}")
        Sleep(900)
        v := ""
        try v := MerFind(GetBravoRoot(), {AutomationId: "BoxReportName"}).Value
        nameOk := (v = name)
        shSel := "", shLog := ""
        Loop 4 {
            s1 := ";"
            pre := CrSelected(MerFind(GetBravoRoot(), {AutomationId: "BoxIsShared"}))
            CrPick(MerFind(GetBravoRoot(), {AutomationId: "BoxIsShared"}), ["Shared Company-Wide"], &s1, true, Mod(A_Index, 2) = 1)
            Sleep(800)
            shSel := CrSelected(MerFind(GetBravoRoot(), {AutomationId: "BoxIsShared"}))
            shV := ""
            try shV := MerFind(GetBravoRoot(), {AutomationId: "BoxIsShared"}).Value
            shLog .= " try" . A_Index . " pre='" . pre . "' sel='" . shSel . "' v='" . shV . "'"
            if (shSel = "Shared Company-Wide")
                break
        }
        out .= "shared attempts:" . shLog . "`r`n"
        sharedOk := (shSel = "Shared Company-Wide")
        s2 := ";"
        lp := CrPick(MerFind(GetBravoRoot(), {AutomationId: "BoxColumns"}), [layoutWant], &s2)
        lv := ""
        try lv := MerFind(GetBravoRoot(), {AutomationId: "BoxColumns"}).Value
        layoutOk := (lp = layoutWant && InStr(lv, "Object_Layout") > 0)
        out .= "name='" . v . "' shared='" . shSel . "' layout pick='" . lp . "' value='" . lv . "'`r`n"
        ; Status
        s3 := ";"
        CrPick(MerFind(GetBravoRoot(), {AutomationId: "BoxSelectCriteria"}), ["Status"], &s3)
        stc := GoInvCriteriaValues("Status", &out)
        statusOk := false
        if stc {
            s4 := ";"
            want := (which = "A") ? ["SOLD"] : ["INVENTORY"]
            CrPick(stc, want, &s4)
            sv := ""
            try sv := CrAfter("Status", "BravoComboBox").Value
            out .= "status value = '" . sv . "'`r`n"
            statusOk := (which = "A") ? (sv = "ITSSLD") : (sv != "" && sv != "ITSSLD")
        }
        extraOk := false
        if (which = "A") {
            ; Status Date range
            s5 := ";"
            CrPick(MerFind(GetBravoRoot(), {AutomationId: "BoxSelectCriteria"}), ["Status Date"], &s5)
            if !InStr(CrRowTexts(), "Status Date | range") {
                lvw := CrList(), op := 0, hit := false
                for k in lvw.GetChildren() {
                    c := "", n := ""
                    try c := k.ClassName
                    try n := k.Name
                    if (!hit) {
                        if (c = "TextBlock" && n = "Status Date")
                            hit := true
                        continue
                    }
                    if (c = "TextBlock") {
                        op := k
                        break
                    }
                }
                if op {
                    h := MerFind(op, {Type: "Hyperlink"})
                    tgt := h ? h : op
                    did := false
                    try {
                        tgt.InvokePattern.Invoke()
                        did := true
                    }
                    if !did
                        tgt.Click("left")
                    Sleep(1800)
                    rg := 0
                    for p in CrPopups() {
                        try rg := p.FindElement({Name: "range", Type: "Text"})
                        if rg
                            break
                    }
                    if rg {
                        rg.Click("left")
                        Sleep(1300)
                    }
                    if (CrPopups().Length > 0) {
                        Send("{Escape}")
                        Sleep(900)
                    }
                }
            }
            d := FormatTime(A_Now, "M/d/yyyy")
            for i, dd in [d, d] {
                des := CrDateEdits()
                if (des.Length != 2)
                    break
                tb := MerFind(des[i], {ClassName: "TextBox"})
                if !tb
                    break
                tb.Click("left")
                Sleep(500)
                Send("^a")
                Sleep(200)
                SendText(dd)
                Sleep(400)
                Send("{Tab}")
                Sleep(700)
            }
            des := CrDateEdits(), dv1 := "", dv2 := ""
            if (des.Length = 2) {
                try dv1 := des[1].Value
                try dv2 := des[2].Value
            }
            datesOk := (InStr(CrRowTexts(), "Status Date | range") && RegExMatch(dv1, "^\d+/\d+/\d{4} 12:00:00 AM") && RegExMatch(dv2, "^\d+/\d+/\d{4} 12:00:00 AM"))
            out .= "dates '" . dv1 . "' '" . dv2 . "' ok=" . datesOk . "`r`n"
            ; Store: record what the value control offers; select every store only when it is a multi-select list
            s6 := ";"
            CrPick(MerFind(GetBravoRoot(), {AutomationId: "BoxSelectCriteria"}), ["Store"], &s6)
            out .= "rows after Store: " . CrRowTexts() . "`r`n"
            spv := 0, hit := false, storeOk := false
            for k in CrList().GetChildren() {
                c := "", n := ""
                try c := k.ClassName
                try n := k.Name
                if (!hit) {
                    if (c = "TextBlock" && n = "Store")
                        hit := true
                    continue
                }
                if (c = "StorePickerView") {
                    spv := k
                    break
                }
            }
            if spv {
                scb := MerFind(spv, {ClassName: "BravoComboBox"})
                arr := scb ? MerFind(scb, {Type: "Button"}) : 0
                if arr {
                    try arr.InvokePattern.Invoke()
                    catch
                        arr.Click("left")
                    Sleep(2200)
                    CrDumpPopups(&out, "store picker list")
                    if (CrPopups().Length > 0) {
                        Send("{Escape}")
                        Sleep(900)
                    }
                }
                ss := ";"
                gotAll := CrPick(scb, ["All stores"], &ss, true, true)
                Sleep(1200)
                if (CrPopups().Length > 0) {
                    Send("{Escape}")
                    Sleep(900)
                }
                selStore := CrSelected(scb)
                stTxt := ""
                for t in spv.FindElements({Type: "Text"}) {
                    n := ""
                    try n := t.Name
                    stTxt .= n . ";"
                }
                out .= "store pick='" . gotAll . "' selected='" . selStore . "' shown='" . stTxt . "'`r`n"
                storeOk := (gotAll = "All stores" && (selStore = "All stores" || InStr(stTxt, "All stores")))
            } else
                out .= "StorePickerView not found`r`n"
            ; the Store value is left as Bravo defaults it; the timing run shows whether rows from other stores come back
            extraOk := datesOk && storeOk
        } else if (which = "C") {
            extraOk := true   ; 2026-11-27 stockbuild: Status = INVENTORY only, no other criterion
        } else {
            s7 := ";"
            CrPick(MerFind(GetBravoRoot(), {AutomationId: "BoxSelectCriteria"}), ["Web Platform"], &s7)
            wpc := GoInvCriteriaValues("Web Platform", &out)
            wpOk := false
            if wpc {
                s8 := ";"
                got := CrPick(wpc, ["eBay", "EBAY", "Ebay", "eBay Auction"], &s8)
                wv := ""
                try wv := CrAfter("Web Platform", "BravoComboBox").Value
                out .= "web platform picked='" . got . "' value='" . wv . "'`r`n"
                wpOk := (got != "")
            }
            extraOk := wpOk
        }
        rows := CrRowTexts()
        out .= "final rows: " . rows . "`r`n"
        lay := MerFind(GetBravoRoot(), {ClassName: "LayoutView"})
        sb := lay ? MerFind(lay, {Name: "Save", Type: "Button"}) : 0
        noUpd := !MerFind(GetBravoRoot(), {Name: "Update", Type: "Button"})
        gate := "name=" . nameOk . " shared=" . sharedOk . " layout=" . layoutOk . " status=" . statusOk . " extra=" . extraOk . " save=" . (sb ? 1 : 0) . " noUpdate=" . noUpd
        out .= "GATE " . gate . "`r`n"
        MerShot(st . "_" . StrLower(tag) . "_1")
        allOk := (nameOk && sharedOk && layoutOk && statusOk && extraOk && sb && noUpd)
        if !allOk
            verdict := "NOSAVE " . gate
        else if !doSave
            verdict := "DRY OK (all checks pass, not saved) " . gate
        else {
            sb.Click("left")
            Sleep(4000)
            MerWaitNotHung(60)
            saved := true
            MerShot(st . "_" . StrLower(tag) . "_2")
            if !MerFind(GetBravoRoot(), {AutomationId: "BoxSelectCriteria"}) {
                DismissPopups()
                cr2 := MerFind(GetBravoRoot(), {Name: "Custom Reports", Type: "Button"})
                if cr2 {
                    cr2.Click("left")
                    Sleep(4000)
                }
            }
            bar := MerFind(GetBravoRoot(), {ClassName: "EntityAdvancedSearchControlBarView"})
            sc := bar ? MerFind(bar, {ClassName: "BravoComboBox"}) : 0
            seen2 := ";"
            have := sc ? CrPick(sc, [name], &seen2, false) : ""
            verdict := (have != "") ? "SAVED+LISTED " . gate : "SAVE CLICKED but not seen in list " . gate
        }
    } catch as e {
        verdict := (saved ? "ERROR AFTER SAVE " : "NOSAVE ") . e.Message
    }
    closed := CrCancelOut(&out)
    MerWrite(outFile, out)
    GoResult(st, tag . " " . verdict . " / dialog " . (closed ? "closed" : "STILL OPEN"))
    try BackToDashboard()
}


; ============================================================================
; layprobe (2026-11-27, Bravo Warehouse, READ ONLY). Runs the existing saved report "Claude Sold Inv Details" exactly
; as saved, then records what the grid's "Layouts" control and a column-header right-click offer, so a new column
; layout ("Claude Item Master") can be designed. Clicks nothing inside those menus; leaves by Escape and Cancel.
; Writes output\inv_reports\<STORE>_layprobe.txt and screenshots <STORE>_layprobe_1..3.png.
; ============================================================================
GoLayProbe(st) {
    global DUMP_COUNT
    if !GoInvOpen() {
        GoResult(st, "LAYPROBE dialog did not open")
        try BackToDashboard()
        return
    }
    out := ""
    bar := MerFind(GetBravoRoot(), {ClassName: "EntityAdvancedSearchControlBarView"})
    sc := bar ? MerFind(bar, {ClassName: "BravoComboBox"}) : 0
    seen := ";"
    got := sc ? CrPick(sc, ["Claude Sold Inv Details"], &seen, true) : ""
    Sleep(2500)
    v := ""
    try v := MerFind(GetBravoRoot(), {AutomationId: "BoxReportName"}).Value
    out .= "selected '" . got . "' name box = '" . v . "'`r`n"
    if !InStr(v, "Claude Sold Inv Details") {
        c0 := ""
        CrCancelOut(&c0)
        MerWrite(OUT_DIR . "\" . st . "_layprobe.txt", out . c0)
        GoResult(st, "LAYPROBE report did not load, cancelled")
        try BackToDashboard()
        return
    }
    okEl := MerFind(GetBravoRoot(), {Name: "Ok", Type: "Text"})
    if okEl {
        r := okEl.BoundingRectangle
        CoordMode("Mouse", "Screen")
        Click((r.l + r.r) // 2, (r.t + r.b) // 2)
    } else
        Send("{Enter}")
    Sleep(4000)
    t0 := A_TickCount
    rows := 0
    Loop {
        try rows := GetBravoRoot().FindElements({Type: "DataItem"}).Length
        if (rows > 0 || A_TickCount - t0 > 90000)
            break
        Sleep(3000)
    }
    out .= "grid rows on screen = " . rows . " after " . ((A_TickCount - t0) // 1000) . "s`r`n"
    Sleep(3000)
    MerShot(st . "_layprobe_1")
    lay := MerFind(GetBravoRoot(), {Name: "Layouts"})
    if lay {
        lr := lay.BoundingRectangle
        out .= "Layouts element at " . lr.l . "," . lr.t . "," . lr.r . "," . lr.b . "`r`n"
        CoordMode("Mouse", "Screen")
        Click((lr.l + lr.r) // 2, (lr.t + lr.b) // 2)
        Sleep(2500)
        MerShot(st . "_layprobe_2")
        CrDumpPopups(&out, "after Layouts click")
        out .= "## root after Layouts click`r`n"
        DUMP_COUNT := 0
        try MerDump(GetBravoRoot(), 0, &out)
        Send("{Escape}")
        Sleep(1200)
    } else
        out .= "## Layouts element not found`r`n"
    hdr := 0
    try hdr := GetBravoRoot().FindElement({Type: "HeaderItem"})
    if hdr {
        hr := hdr.BoundingRectangle
        hn := ""
        try hn := hdr.Name
        out .= "first header '" . hn . "' at " . hr.l . "," . hr.t . "," . hr.r . "," . hr.b . "`r`n"
        CoordMode("Mouse", "Screen")
        Click((hr.l + hr.r) // 2, (hr.t + hr.b) // 2, "Right")
        Sleep(2000)
        MerShot(st . "_layprobe_3")
        CrDumpPopups(&out, "after header right-click")
        Send("{Escape}")
        Sleep(1200)
    } else
        out .= "## no HeaderItem found`r`n"
    Loop 3 {
        c := MerFind(GetBravoRoot(), {Name: "Cancel", Type: "Button"})
        if !c
            break
        c.Click("left")
        Sleep(2000)
    }
    MerWrite(OUT_DIR . "\" . st . "_layprobe.txt", out)
    GoResult(st, "LAYPROBE done (nothing saved)")
    try BackToDashboard()
}

; layprobe2 (2026-11-27, Bravo Warehouse, READ ONLY). Same as layprobe, then opens the Layouts expander and the grid's
; Column Chooser, records what each shows, closes both and leaves by Cancel. Nothing is saved, no layout is changed.
; Writes output\inv_reports\<STORE>_layprobe2.txt and full-resolution screenshots <STORE>_layprobe2_1..4.png.
LayShot(key) {
    png := OUT_DIR . "\" . key . ".png"
    cmd := "powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"" . A_ScriptDir . "\layshot.ps1`" `"" . png . "`""
    try RunWait(cmd, , "Hide")
}

LayDumpSkipGrid(el, depth, &out) {
    global DUMP_COUNT
    c := ""
    try c := el.ClassName
    if (c = "InventoryItemsGridView") {
        out .= "  (grid skipped)`r`n"
        return
    }
    if (depth > 30 || DUMP_COUNT > 4000)
        return
    DUMP_COUNT += 1
    t := "", n := "", rs := "", v := "", tg := ""
    try t := el.LocalizedType
    try n := el.Name
    try {
        r := el.BoundingRectangle
        rs := r.l . "," . r.t . "," . r.r . "," . r.b
    }
    try v := el.Value
    try tg := String(el.ToggleState)
    ind := ""
    Loop depth
        ind .= "  "
    line := ind . "[" . t . "] N=" . MerClean(n, 200) . " | C=" . MerClean(c, 80) . " | R=" . rs
    if (tg != "")
        line .= " | TOGGLE=" . tg
    if (v != "")
        line .= " | V=" . MerClean(v, 200)
    out .= line . "`r`n"
    kids := []
    try kids := el.GetChildren()
    for k in kids
        LayDumpSkipGrid(k, depth + 1, &out)
}

LayDumpWindows(&out, label) {
    global DUMP_COUNT
    out .= "## other Bravo windows: " . label . "`r`n"
    mainHwnd := WinExist(BRAVO_WIN_TITLE)
    for hwnd in WinGetList("ahk_exe Bravo.exe") {
        if (hwnd = mainHwnd || !DllCall("IsWindowVisible", "ptr", hwnd, "int"))
            continue
        el := 0
        try el := UIA.ElementFromHandle(hwnd)
        if !el
            continue
        DUMP_COUNT := 0
        try MerDump(el, 0, &out)
    }
}

GoLayProbe2(st) {
    global DUMP_COUNT
    if !GoInvOpen() {
        GoResult(st, "LAYPROBE2 dialog did not open")
        try BackToDashboard()
        return
    }
    out := ""
    bar := MerFind(GetBravoRoot(), {ClassName: "EntityAdvancedSearchControlBarView"})
    sc := bar ? MerFind(bar, {ClassName: "BravoComboBox"}) : 0
    seen := ";"
    got := sc ? CrPick(sc, ["Claude Sold Inv Details"], &seen, true) : ""
    Sleep(2500)
    v := ""
    try v := MerFind(GetBravoRoot(), {AutomationId: "BoxReportName"}).Value
    out .= "selected '" . got . "' name box = '" . v . "'`r`n"
    if !InStr(v, "Claude Sold Inv Details") {
        c0 := ""
        CrCancelOut(&c0)
        MerWrite(OUT_DIR . "\" . st . "_layprobe2.txt", out . c0)
        GoResult(st, "LAYPROBE2 report did not load, cancelled")
        try BackToDashboard()
        return
    }
    okEl := MerFind(GetBravoRoot(), {Name: "Ok", Type: "Text"})
    if okEl {
        r := okEl.BoundingRectangle
        CoordMode("Mouse", "Screen")
        Click((r.l + r.r) // 2, (r.t + r.b) // 2)
    } else
        Send("{Enter}")
    Sleep(4000)
    t0 := A_TickCount
    rows := 0
    Loop {
        try rows := GetBravoRoot().FindElements({Type: "DataItem"}).Length
        if (rows > 0 || A_TickCount - t0 > 90000)
            break
        Sleep(3000)
    }
    out .= "grid rows on screen = " . rows . " after " . ((A_TickCount - t0) // 1000) . "s`r`n"
    Sleep(3000)
    LayShot(st . "_layprobe2_1")
    ; ---- Layouts expander ----
    ex := MerFind(GetBravoRoot(), {ClassName: "Expander"})
    if ex {
        er := ex.BoundingRectangle
        out .= "Expander at " . er.l . "," . er.t . "," . er.r . "," . er.b . "`r`n"
        CoordMode("Mouse", "Screen")
        Click((er.l + er.r) // 2, (er.t + er.b) // 2)
        Sleep(3000)
        LayShot(st . "_layprobe2_2")
        CrDumpPopups(&out, "after expander click")
        LayDumpWindows(&out, "after expander click")
        out .= "## root (grid skipped) after expander click`r`n"
        DUMP_COUNT := 0
        try LayDumpSkipGrid(GetBravoRoot(), 0, &out)
        ; collapse again: same spot if the expander is still there and grew, else Escape
        ex2 := MerFind(GetBravoRoot(), {ClassName: "Expander"})
        if ex2 {
            e2 := ex2.BoundingRectangle
            out .= "Expander after click at " . e2.l . "," . e2.t . "," . e2.r . "," . e2.b . "`r`n"
            Click((er.l + er.r) // 2, (er.t + er.b) // 2)
        } else
            Send("{Escape}")
        Sleep(2000)
    } else
        out .= "## Expander not found`r`n"
    ; ---- Column Chooser ----
    hdr := 0
    try hdr := GetBravoRoot().FindElement({Type: "HeaderItem"})
    if hdr {
        hr := hdr.BoundingRectangle
        CoordMode("Mouse", "Screen")
        Click((hr.l + hr.r) // 2, (hr.t + hr.b) // 2, "Right")
        Sleep(2000)
        cc := 0
        for p in CrPopups() {
            try cc := p.FindElement({Name: "Show Column Chooser"})
            if cc
                break
        }
        if cc {
            cr := cc.BoundingRectangle
            Click((cr.l + cr.r) // 2, (cr.t + cr.b) // 2)
            Sleep(3500)
            LayShot(st . "_layprobe2_3")
            CrDumpPopups(&out, "column chooser open")
            LayDumpWindows(&out, "column chooser open")
            out .= "## root (grid skipped) with column chooser open`r`n"
            DUMP_COUNT := 0
            try LayDumpSkipGrid(GetBravoRoot(), 0, &out)
            ; close it again through the same menu
            try hdr := GetBravoRoot().FindElement({Type: "HeaderItem"})
            hr := hdr.BoundingRectangle
            Click((hr.l + hr.r) // 2, (hr.t + hr.b) // 2, "Right")
            Sleep(2000)
            hc := 0
            names := ""
            for p in CrPopups() {
                try {
                    for b in p.FindElements({ClassName: "LightweightBarItemLinkControl"}) {
                        nm := ""
                        try nm := b.Name
                        names .= nm . "; "
                        if InStr(nm, "Column Chooser")
                            hc := b
                    }
                }
            }
            out .= "menu with chooser open: " . names . "`r`n"
            if (hc && InStr(hc.Name, "Hide")) {
                xr := hc.BoundingRectangle
                Click((xr.l + xr.r) // 2, (xr.t + xr.b) // 2)
                out .= "chooser closed by menu`r`n"
            } else {
                Send("{Escape}")
                out .= "chooser NOT closed by menu (no Hide item)`r`n"
            }
            Sleep(2000)
            LayShot(st . "_layprobe2_4")
        } else {
            out .= "## Show Column Chooser not found in menu`r`n"
            Send("{Escape}")
            Sleep(1000)
        }
    } else
        out .= "## no HeaderItem found`r`n"
    Loop 3 {
        c := MerFind(GetBravoRoot(), {Name: "Cancel", Type: "Button"})
        if !c
            break
        c.Click("left")
        Sleep(2000)
    }
    MerWrite(OUT_DIR . "\" . st . "_layprobe2.txt", out)
    GoResult(st, "LAYPROBE2 done (nothing saved)")
    try BackToDashboard()
}

; layprobe3 (2026-11-27, Bravo Warehouse, READ ONLY). Opens the Layouts drop-down beside the grid and records it, closes it,
; then opens the Column Chooser and records every column name with its ticked state, closes it, leaves by Cancel. Nothing saved.
LayOpenReport(st, tag, &out) {
    if !GoInvOpen()
        return false
    bar := MerFind(GetBravoRoot(), {ClassName: "EntityAdvancedSearchControlBarView"})
    sc := bar ? MerFind(bar, {ClassName: "BravoComboBox"}) : 0
    seen := ";"
    got := sc ? CrPick(sc, ["Claude Sold Inv Details"], &seen, true) : ""
    Sleep(2500)
    v := ""
    try v := MerFind(GetBravoRoot(), {AutomationId: "BoxReportName"}).Value
    out .= "selected '" . got . "' name box = '" . v . "'`r`n"
    if !InStr(v, "Claude Sold Inv Details") {
        c0 := ""
        CrCancelOut(&c0)
        out .= c0
        return false
    }
    okEl := MerFind(GetBravoRoot(), {Name: "Ok", Type: "Text"})
    if okEl {
        r := okEl.BoundingRectangle
        CoordMode("Mouse", "Screen")
        Click((r.l + r.r) // 2, (r.t + r.b) // 2)
    } else
        Send("{Enter}")
    Sleep(4000)
    t0 := A_TickCount
    rows := 0
    Loop {
        try rows := GetBravoRoot().FindElements({Type: "DataItem"}).Length
        if (rows > 0 || A_TickCount - t0 > 90000)
            break
        Sleep(3000)
    }
    out .= "grid rows on screen = " . rows . " after " . ((A_TickCount - t0) // 1000) . "s`r`n"
    Sleep(3000)
    return rows > 0
}

LayChooserWin() {
    for hwnd in WinGetList("ahk_exe Bravo.exe") {
        if !DllCall("IsWindowVisible", "ptr", hwnd, "int")
            continue
        el := 0
        try el := UIA.ElementFromHandle(hwnd)
        if !el
            continue
        n := ""
        try n := el.Name
        if (n = "Column Chooser")
            return el
    }
    return 0
}

GoLayProbe3(st) {
    global DUMP_COUNT
    out := ""
    if !LayOpenReport(st, "layprobe3", &out) {
        MerWrite(OUT_DIR . "\" . st . "_layprobe3.txt", out)
        GoResult(st, "LAYPROBE3 report did not open")
        Loop 3 {
            c := MerFind(GetBravoRoot(), {Name: "Cancel", Type: "Button"})
            if !c
                break
            c.Click("left")
            Sleep(2000)
        }
        try BackToDashboard()
        return
    }
    CoordMode("Mouse", "Screen")
    ; ---- Layouts drop-down: the Expander just right of the "Layouts" label ----
    lay := MerFind(GetBravoRoot(), {Name: "Layouts"})
    ex := 0
    if lay {
        lr := lay.BoundingRectangle
        try {
            for e in GetBravoRoot().FindElements({ClassName: "Expander"}) {
                er := e.BoundingRectangle
                if (er.l >= lr.r - 5 && er.l <= lr.r + 200 && Abs(er.t - lr.t) < 60)
                    ex := e
            }
        }
    }
    if ex {
        er := ex.BoundingRectangle
        out .= "Layouts expander at " . er.l . "," . er.t . "," . er.r . "," . er.b . "`r`n"
        cx := (er.l + er.r) // 2, cy := (er.t + er.b) // 2
        Click(cx, cy)
        Sleep(3000)
        LayShot(st . "_layprobe3_1")
        CrDumpPopups(&out, "after Layouts expander click")
        out .= "## root (grid skipped) after Layouts expander click`r`n"
        DUMP_COUNT := 0
        try LayDumpSkipGrid(GetBravoRoot(), 0, &out)
        ; close: Escape first, and if a popup is still there click the expander again
        Send("{Escape}")
        Sleep(1500)
        if (CrPopups().Length > 0) {
            Click(cx, cy)
            Sleep(1500)
        }
        out .= "popups left after closing = " . CrPopups().Length . "`r`n"
        LayShot(st . "_layprobe3_2")
    } else
        out .= "## Layouts expander not found`r`n"
    ; ---- Column Chooser: every column name and state ----
    hdr := 0
    try hdr := GetBravoRoot().FindElement({Type: "HeaderItem"})
    if hdr {
        hr := hdr.BoundingRectangle
        Click((hr.l + hr.r) // 2, (hr.t + hr.b) // 2, "Right")
        Sleep(2000)
        cc := 0
        for p in CrPopups() {
            try cc := p.FindElement({Name: "Show Column Chooser"})
            if cc
                break
        }
        if cc {
            cr := cc.BoundingRectangle
            Click((cr.l + cr.r) // 2, (cr.t + cr.b) // 2)
            Sleep(3500)
            win := LayChooserWin()
            if win {
                wr := win.BoundingRectangle
                out .= "## column chooser columns (name = state)`r`n"
                seenN := Map()
                MouseMove((wr.l + wr.r) // 2, (wr.t + wr.b) // 2 + 60)
                Loop 30 {
                    added := 0
                    try {
                        for it in win.FindElements({Type: "TreeItem"}) {
                            nm := "", stt := ""
                            try nm := it.FindElement({Type: "Text"}).Name
                            try stt := it.FindElement({ClassName: "CheckEdit"}).Value
                            if (nm != "" && !seenN.Has(nm)) {
                                seenN[nm] := 1
                                out .= nm . " = " . stt . "`r`n"
                                added += 1
                            }
                        }
                    }
                    Send("{WheelDown 3}")
                    Sleep(700)
                    if (added = 0 && A_Index > 3)
                        break
                }
                out .= "columns read = " . seenN.Count . "`r`n"
                LayShot(st . "_layprobe3_3")
            } else
                out .= "## column chooser window not found`r`n"
            try hdr := GetBravoRoot().FindElement({Type: "HeaderItem"})
            hr := hdr.BoundingRectangle
            Click((hr.l + hr.r) // 2, (hr.t + hr.b) // 2, "Right")
            Sleep(2000)
            hc := 0
            for p in CrPopups() {
                try hc := p.FindElement({Name: "Hide Column Chooser"})
                if hc
                    break
            }
            if hc {
                xr := hc.BoundingRectangle
                Click((xr.l + xr.r) // 2, (xr.t + xr.b) // 2)
                out .= "chooser closed by menu`r`n"
            } else {
                Send("{Escape}")
                out .= "chooser NOT closed by menu`r`n"
            }
            Sleep(2000)
        } else {
            out .= "## Show Column Chooser not found`r`n"
            Send("{Escape}")
            Sleep(1000)
        }
    }
    Loop 3 {
        c := MerFind(GetBravoRoot(), {Name: "Cancel", Type: "Button"})
        if !c
            break
        c.Click("left")
        Sleep(2000)
    }
    MerWrite(OUT_DIR . "\" . st . "_layprobe3.txt", out)
    GoResult(st, "LAYPROBE3 done (nothing saved)")
    try BackToDashboard()
}

; laydry / laybuild (2026-11-27, Bravo Warehouse). ADDITIVE: creates ONE new shared grid layout "Claude Item Master" for
; Inventory custom reports. Opens the existing report "Claude Sold Inv Details" (not changed), ticks the extra columns in the
; Column Chooser, types the new layout name and presses "Save" (never "Update", never "Delete Layout"). laydry does everything
; except press Save. Every gate must pass or nothing is saved. Leaves by Cancel.
LayName() {
    return "Claude Item Master"
}
LayWant() {
    return ["Number", "Status", "Category", "Description", "Cost", "Price", "Last Sold Price", "Date", "Store", "Source", "Type", "Last Ticket Number", "Date to Inventory", "Inventory Age", "Quantity", "Sale Price", "Location", "Vendor", "Customer", "Last Sold To", "Metal Type/Color", "Metal Purity", "Metal Weight", "Total Jewelry Weight", "Serial Number", "Manufacturer", "Model", "Reference Number", "Invoice #", "SKU Number", "Quality"]
}

LayWantHas(nm) {
    for w in LayWant()
        if (w = nm)
            return true
    return false
}

; walks the chooser top to bottom. doTick: ticks wanted columns that are off. Returns Map(name -> "True"/"False") as last seen.
LayChooserPass(win, doTick, &log) {
    states := Map()
    wr := win.BoundingRectangle
    MouseMove((wr.l + wr.r) // 2, (wr.t + wr.b) // 2 + 60)
    Send("{WheelUp 80}")
    Sleep(1200)
    idle := 0
    Loop 40 {
        added := 0
        items := []
        try items := win.FindElements({Type: "TreeItem"})
        for it in items {
            nm := "", stt := "", cb := 0
            try nm := it.FindElement({Type: "Text"}).Name
            try cb := it.FindElement({ClassName: "CheckEdit"})
            if (nm = "" || !cb)
                continue
            try stt := cb.Value
            if !states.Has(nm)
                added += 1
            if (doTick && LayWantHas(nm) && stt = "False") {
                cr := cb.BoundingRectangle
                if (cr.t >= wr.t + 120 && cr.b <= wr.b - 14) {
                    Click((cr.l + cr.r) // 2, (cr.t + cr.b) // 2)
                    Sleep(900)
                    try stt := cb.Value
                    log .= "ticked " . nm . " -> " . stt . "`r`n"
                    MouseMove((wr.l + wr.r) // 2, (wr.t + wr.b) // 2 + 60)
                }
            }
            states[nm] := stt
        }
        idle := (added = 0) ? idle + 1 : 0
        if (idle >= 3)
            break
        Send("{WheelDown 2}")
        Sleep(700)
    }
    return states
}

LayOpenChooser() {
    hdr := 0
    try hdr := GetBravoRoot().FindElement({Type: "HeaderItem"})
    if !hdr
        return 0
    hr := hdr.BoundingRectangle
    Click((hr.l + hr.r) // 2, (hr.t + hr.b) // 2, "Right")
    Sleep(2000)
    cc := 0
    for p in CrPopups() {
        try cc := p.FindElement({Name: "Show Column Chooser"})
        if cc
            break
    }
    if !cc {
        Send("{Escape}")
        Sleep(800)
        return 0
    }
    cr := cc.BoundingRectangle
    Click((cr.l + cr.r) // 2, (cr.t + cr.b) // 2)
    Sleep(3500)
    return LayChooserWin()
}

LayCloseChooser() {
    win := LayChooserWin()
    if !win
        return true
    cb := 0
    try cb := win.FindElement({Name: "Close", Type: "Button"})
    if cb {
        r := cb.BoundingRectangle
        Click((r.l + r.r) // 2, (r.t + r.b) // 2)
        Sleep(1500)
    }
    return !LayChooserWin()
}

; opens a combo by clicking its arrow, records the popup, returns ";name;name;" of its text items, closes with Escape.
LayList(combo, &out, label) {
    global DUMP_COUNT
    seen := ";"
    arrow := 0
    try arrow := combo.FindElement({Type: "Button"})
    if !arrow {
        out .= label . ": no arrow`r`n"
        return seen
    }
    ar := arrow.BoundingRectangle
    Click((ar.l + ar.r) // 2, (ar.t + ar.b) // 2)
    Sleep(2500)
    pops := CrPopups()
    out .= "## " . label . ": popups=" . pops.Length . "`r`n"
    for p in pops {
        DUMP_COUNT := 0
        try MerDump(p, 0, &out)
        try {
            for t in p.FindElements({Type: "Text"}) {
                n := ""
                try n := t.Name
                if (n != "" && !InStr(seen, ";" . n . ";"))
                    seen .= n . ";"
            }
        }
    }
    if (CrPopups().Length > 0) {
        Send("{Escape}")
        Sleep(1000)
    }
    if (CrPopups().Length > 0) {
        Click((ar.l + ar.r) // 2, (ar.t + ar.b) // 2)
        Sleep(1000)
    }
    out .= label . " = " . seen . "`r`n"
    return seen
}
LayAll() {
    return ["Action", "Address", "Age", "Area", "Authentic-Diamond Jewelry", "Authentic-Stone Jewelry", "Barcode", "Barcode Image", "Buya Delivery Amount", "Caliber", "Category", "Cost", "Customer", "Date", "Date to Inventory", "Description", "eBay Delivery Option", "E-Mail", "Image Kind", "Inventory Age", "Invoice #", "Last Sold Price", "Last Sold To", "Last Sold To Address", "Last Sold To E-Mail", "Last Sold To Phone", "Last Ticket Number", "Location", "Manufacturer", "Max Discount", "Metal Purity", "Metal Type/Color", "Metal Weight", "Model", "Notes", "Number", "Owner Applied Number", "Phone", "Price", "Quality", "Quantity", "Reference Number", "Sale Price", "Serial Number", "SKU Number", "Source", "Status", "Store", "Total Diamond Size", "Total Jewelry Weight", "Total Stone Size", "Type", "UPC", "Vendor", "Vendor Address", "Vendor E-Mail", "Vendor Phone", "Web Delivery Option", "Web Price", "Web URL"]
}

; sets one chooser column through the search box. Returns the state read afresh afterwards ("True"/"False"/"" when not found).
LaySetColumn(win, nm, wantOn, doClick, &log) {
    sb := 0
    try sb := win.FindElement({ClassName: "TextBox"})
    if !sb
        return ""
    r := sb.BoundingRectangle
    Click((r.l + r.r) // 2, (r.t + r.b) // 2)
    Sleep(350)
    Send("^a")
    Sleep(150)
    SendText(nm)
    Sleep(1300)
    res := ""
    Loop 2 {
        pass := A_Index
        hit := 0
        try {
            for it in win.FindElements({Type: "TreeItem"}) {
                t := ""
                try t := it.FindElement({Type: "Text"}).Name
                if (t = nm) {
                    hit := it
                    break
                }
            }
        }
        if !hit
            return ""
        cb := 0
        try cb := hit.FindElement({ClassName: "CheckEdit"})
        if !cb
            return ""
        res := ""
        try res := cb.Value
        want := wantOn ? "True" : "False"
        if (res = want || !doClick || pass = 2)
            break
        cr := cb.BoundingRectangle
        Click((cr.l + cr.r) // 2, (cr.t + cr.b) // 2)
        Sleep(1000)
        log .= "set " . nm . " -> " . want . "`r`n"
    }
    return res
}

; every one of the 60 columns: set (doClick) or just read. Returns the count that match the wanted layout; bad lists the rest.
LayApplyColumns(win, doClick, &log, &bad) {
    okN := 0
    bad := ""
    for nm in LayAll() {
        want := LayWantHas(nm)
        got := LaySetColumn(win, nm, want, doClick, &log)
        if (got = "") {
            Sleep(1500)
            got := LaySetColumn(win, nm, want, doClick, &log)
        }
        if (got = (want ? "True" : "False"))
            okN += 1
        else
            bad .= nm . "=" . got . " "
    }
    sb := 0
    try sb := win.FindElement({ClassName: "TextBox"})
    if sb {
        r := sb.BoundingRectangle
        Click((r.l + r.r) // 2, (r.t + r.b) // 2)
        Sleep(300)
        Send("^a")
        Sleep(150)
        Send("{Delete}")
        Sleep(800)
    }
    return okN
}

; the chevron button right of the "Layouts" label (its ToggleState is 1 while the layout panel is open)
LayExpanderBtn() {
    lay := MerFind(GetBravoRoot(), {Name: "Layouts"})
    if !lay
        return 0
    lr := lay.BoundingRectangle
    ex := 0
    try {
        for e in GetBravoRoot().FindElements({ClassName: "Expander"}) {
            er := e.BoundingRectangle
            if (er.l >= lr.r - 5 && er.l <= lr.r + 200 && Abs(er.t - lr.t) < 60)
                ex := e
        }
    }
    if !ex
        return 0
    b := 0
    try b := ex.FindElement({Type: "Button"})
    return b
}

LayPanelIsOpen() {
    b := LayExpanderBtn()
    if !b
        return false
    ts := ""
    try ts := String(b.ToggleState)
    return ts = "1"
}

LayPanel() {
    if !LayPanelIsOpen()
        return 0
    return MerFind(GetBravoRoot(), {ClassName: "InplaceGridLayoutManagementView"})
}

LayOpenPanel() {
    if LayPanelIsOpen()
        return LayPanel() ? true : false
    b := LayExpanderBtn()
    if !b
        return false
    r := b.BoundingRectangle
    Click((r.l + r.r) // 2, (r.t + r.b) // 2)
    Sleep(3000)
    return LayPanel() ? true : false
}

GoLayBuild(st, doSave) {
    global DUMP_COUNT
    LAY_NAME := LayName()
    LAY_WANT := LayWant()
    tag := doSave ? "LAYBUILD" : "LAYDRY"
    out := ""
    outFile := OUT_DIR . "\" . st . "_" . StrLower(tag) . ".txt"
    verdict := "NOSAVE not reached"
    saved := false
    try {
        if !LayOpenReport(st, tag, &out)
            throw Error("report did not open")
        CoordMode("Mouse", "Screen")
        ; 0. the name must not exist yet
        if !LayOpenPanel()
            throw Error("layout panel did not open")
        pnl := LayPanel()
        combos := pnl.FindElements({ClassName: "BravoComboBox"})
        ; the wide combo under the name box is Saved Layouts; the narrow one right of the name box is the sharing choice
        savedCb := 0, shareCb := 0
        for c in combos {
            r := c.BoundingRectangle
            if (r.r - r.l > 600)
                savedCb := c
            else
                shareCb := c
        }
        if (!savedCb || !shareCb)
            throw Error("layout panel combos not found")
        seenL := LayList(savedCb, &out, "saved layouts")
        shDbg := LayList(shareCb, &out, "sharing choices")
        out .= "saved layouts before: " . seenL . "`r`n"
        if InStr(seenL, ";" . LAY_NAME . ";")
            throw Error("layout already exists")
        listOk := InStr(seenL, ";Sold inv detail;") > 0
        if (!listOk && doSave)
            throw Error("saved layout list unreadable")
        ; 1. tick the columns
        win := LayOpenChooser()
        if !win
            throw Error("column chooser did not open")
        tl := "", bad1 := "", bad := ""
        LayApplyColumns(win, true, &tl, &bad1)
        out .= tl . "after set pass, not matching: '" . bad1 . "'`r`n"
        tl2 := ""
        okN := LayApplyColumns(win, false, &tl2, &bad)
        colsOk := (okN = 60 && bad = "")
        out .= "verify pass: matching=" . okN . " of 60, not matching: '" . bad . "'`r`n"
        LayShot(st . "_" . StrLower(tag) . "_1")
        chClosed := LayCloseChooser()
        out .= "chooser closed=" . chClosed . "`r`n"
        hdrN := 0
        try hdrN := GetBravoRoot().FindElements({Type: "HeaderItem"}).Length
        out .= "grid header items now=" . hdrN . "`r`n"
        ; 2. name + sharing
        if !LayOpenPanel()
            throw Error("layout panel did not reopen")
        pnl := LayPanel()
        nb := pnl.FindElement({ClassName: "BravoMaskedTextBox"})
        nr := nb.BoundingRectangle
        if ((nr.r - nr.l) < 100 || nr.t < 100)
            throw Error("name box not on screen")
        Click((nr.l + nr.r) // 2, (nr.t + nr.b) // 2)
        Sleep(500)
        Send("^a")
        Sleep(300)
        SendText(LAY_NAME)
        Sleep(700)
        Send("{Tab}")
        Sleep(900)
        pnl := LayPanel()
        v := ""
        try v := pnl.FindElement({ClassName: "BravoMaskedTextBox"}).Value
        nameOk := (v = LAY_NAME)
        savedCb := 0, shareCb := 0
        for c in pnl.FindElements({ClassName: "BravoComboBox"}) {
            r := c.BoundingRectangle
            if (r.r - r.l > 600)
                savedCb := c
            else
                shareCb := c
        }
        shSel := CrSelected(shareCb)
        if (shSel != "Shared Company-Wide") {
            s1 := ";"
            CrPick(shareCb, ["Shared Company-Wide"], &s1, true)
            Sleep(800)
            shSel := CrSelected(shareCb)
        }
        sharedOk := (shSel = "Shared Company-Wide")
        v2 := ""
        try v2 := LayPanel().FindElement({ClassName: "BravoMaskedTextBox"}).Value
        nameOk := nameOk && (v2 = LAY_NAME)
        sb := MerFind(LayPanel(), {Name: "Save", Type: "Button"})
        gate := "name=" . nameOk . " shared=" . sharedOk . " cols=" . colsOk . " chooserClosed=" . chClosed . " save=" . (sb ? 1 : 0) . " list=" . listOk
        out .= "name box='" . v2 . "' sharing='" . shSel . "'`r`nGATE " . gate . "`r`n"
        LayShot(st . "_" . StrLower(tag) . "_2")
        allOk := (nameOk && sharedOk && colsOk && chClosed && sb && listOk)
        if !allOk
            verdict := "NOSAVE " . gate
        else if !doSave
            verdict := "DRY OK (all checks pass, not saved) " . gate
        else {
            sr := sb.BoundingRectangle
            Click((sr.l + sr.r) // 2, (sr.t + sr.b) // 2)
            saved := true
            Sleep(5000)
            MerWaitNotHung(60)
            LayShot(st . "_" . StrLower(tag) . "_3")
            CrDumpPopups(&out, "after Save")
            if !LayOpenPanel()
                throw Error("panel gone after save")
            pnl := LayPanel()
            savedCb := 0
            for c in pnl.FindElements({ClassName: "BravoComboBox"}) {
                r := c.BoundingRectangle
                if (r.r - r.l > 600)
                    savedCb := c
            }
            seenA := LayList(savedCb, &out, "saved layouts after save")
            out .= "saved layouts after: " . seenA . "`r`n"
            hasNew := InStr(seenA, ";" . LAY_NAME . ";") > 0
            hasOld := InStr(seenA, ";Sold inv detail;") > 0
            verdict := (hasNew && hasOld) ? "SAVED+LISTED " . gate : "SAVE CLICKED new=" . hasNew . " old=" . hasOld . " " . gate
        }
    } catch as e {
        verdict := (saved ? "ERROR AFTER SAVE " : "NOSAVE ") . e.Message
    }
    try LayCloseChooser()
    if (CrPopups().Length > 0) {
        Send("{Escape}")
        Sleep(900)
    }
    Loop 3 {
        c := MerFind(GetBravoRoot(), {Name: "Cancel", Type: "Button"})
        if !c
            break
        c.Click("left")
        Sleep(2000)
    }
    MerWrite(outFile, out)
    GoResult(st, tag . " " . verdict)
    try BackToDashboard()
}

; itemdry / itembuild (2026-11-27, Bravo Warehouse). ADDITIVE clone of GoInvBuild "A": ONE new saved report
; "Claude Item Master": layout "Claude Item Master", Shared Company-Wide, Status Date range, Store, and NO Status
; criterion so items in every status come back. itemdry leaves by Cancel; itembuild presses Save only when every gate passes.
GoItemBuild(st, doSave) {
    which := "A"
    global DUMP_COUNT
    name := "Claude Item Master"
    layoutWant := "Claude Item Master"
    tag := doSave ? "ITEMBUILD" : "ITEMDRY"
    out := ""
    outFile := OUT_DIR . "\" . st . "_" . StrLower(tag) . ".txt"
    if !GoInvOpen() {
        GoResult(st, tag . " dialog did not open")
        try BackToDashboard()
        return
    }
    verdict := "", saved := false
    try {
        bar := MerFind(GetBravoRoot(), {ClassName: "EntityAdvancedSearchControlBarView"})
        sc := bar ? MerFind(bar, {ClassName: "BravoComboBox"}) : 0
        if !sc
            throw Error("saved-report list not found")
        seen := ";", have := ""
        Loop 3 {
            have := CrPick(sc, [name], &seen, false)
            if (have != "" || StrLen(seen) >= 20)
                break
            Sleep(2000)
        }
        if (have != "")
            throw Error("ALREADY EXISTS - nothing to do")
        if (StrLen(seen) < 20)
            throw Error("saved-report list could not be read")
        nr := MerFind(GetBravoRoot(), {Name: "New Report", Type: "Button"})
        if !nr
            throw Error("New Report button not found")
        nr.Click("left")
        Sleep(2500)
        nb := MerFind(GetBravoRoot(), {AutomationId: "BoxReportName"})
        if !nb
            throw Error("report name box not found")
        v := ""
        try v := nb.Value
        if (v != "" || CrRowTexts() != "")
            throw Error("form not blank after New Report")
        if MerFind(GetBravoRoot(), {Name: "Update", Type: "Button"})
            throw Error("Update button present - an existing report is loaded")
        inner := MerFind(nb, {ClassName: "TextBox"})
        (inner ? inner : nb).Click("left")
        Sleep(500)
        Send("^a")
        Sleep(200)
        SendText(name)
        Sleep(500)
        Send("{Tab}")
        Sleep(900)
        v := ""
        try v := MerFind(GetBravoRoot(), {AutomationId: "BoxReportName"}).Value
        nameOk := (v = name)
        shSel := "", shLog := ""
        Loop 4 {
            s1 := ";"
            pre := CrSelected(MerFind(GetBravoRoot(), {AutomationId: "BoxIsShared"}))
            CrPick(MerFind(GetBravoRoot(), {AutomationId: "BoxIsShared"}), ["Shared Company-Wide"], &s1, true, Mod(A_Index, 2) = 1)
            Sleep(800)
            shSel := CrSelected(MerFind(GetBravoRoot(), {AutomationId: "BoxIsShared"}))
            shV := ""
            try shV := MerFind(GetBravoRoot(), {AutomationId: "BoxIsShared"}).Value
            shLog .= " try" . A_Index . " pre='" . pre . "' sel='" . shSel . "' v='" . shV . "'"
            if (shSel = "Shared Company-Wide")
                break
        }
        out .= "shared attempts:" . shLog . "`r`n"
        sharedOk := (shSel = "Shared Company-Wide")
        s2 := ";"
        lp := CrPick(MerFind(GetBravoRoot(), {AutomationId: "BoxColumns"}), [layoutWant], &s2)
        lv := ""
        try lv := MerFind(GetBravoRoot(), {AutomationId: "BoxColumns"}).Value
        layoutOk := (lp = layoutWant && InStr(lv, "Object_Layout") > 0)
        out .= "name='" . v . "' shared='" . shSel . "' layout pick='" . lp . "' value='" . lv . "'`r`n"
        ; no Status criterion: every status comes back (sold, scrapped, transferred, in stock ...)
        statusOk := !InStr(CrRowTexts(), "Status |")
        extraOk := false
        if (which = "A") {
            ; Status Date range
            s5 := ";"
            CrPick(MerFind(GetBravoRoot(), {AutomationId: "BoxSelectCriteria"}), ["Status Date"], &s5)
            if !InStr(CrRowTexts(), "Status Date | range") {
                lvw := CrList(), op := 0, hit := false
                for k in lvw.GetChildren() {
                    c := "", n := ""
                    try c := k.ClassName
                    try n := k.Name
                    if (!hit) {
                        if (c = "TextBlock" && n = "Status Date")
                            hit := true
                        continue
                    }
                    if (c = "TextBlock") {
                        op := k
                        break
                    }
                }
                if op {
                    h := MerFind(op, {Type: "Hyperlink"})
                    tgt := h ? h : op
                    did := false
                    try {
                        tgt.InvokePattern.Invoke()
                        did := true
                    }
                    if !did
                        tgt.Click("left")
                    Sleep(1800)
                    rg := 0
                    for p in CrPopups() {
                        try rg := p.FindElement({Name: "range", Type: "Text"})
                        if rg
                            break
                    }
                    if rg {
                        rg.Click("left")
                        Sleep(1300)
                    }
                    if (CrPopups().Length > 0) {
                        Send("{Escape}")
                        Sleep(900)
                    }
                }
            }
            d := FormatTime(A_Now, "M/d/yyyy")
            for i, dd in [d, d] {
                des := CrDateEdits()
                if (des.Length != 2)
                    break
                tb := MerFind(des[i], {ClassName: "TextBox"})
                if !tb
                    break
                tb.Click("left")
                Sleep(500)
                Send("^a")
                Sleep(200)
                SendText(dd)
                Sleep(400)
                Send("{Tab}")
                Sleep(700)
            }
            des := CrDateEdits(), dv1 := "", dv2 := ""
            if (des.Length = 2) {
                try dv1 := des[1].Value
                try dv2 := des[2].Value
            }
            datesOk := (InStr(CrRowTexts(), "Status Date | range") && RegExMatch(dv1, "^\d+/\d+/\d{4} 12:00:00 AM") && RegExMatch(dv2, "^\d+/\d+/\d{4} 12:00:00 AM"))
            out .= "dates '" . dv1 . "' '" . dv2 . "' ok=" . datesOk . "`r`n"
            ; no Store criterion: the pull runs store by store like every other handler
            extraOk := datesOk && (CrRowTexts() = "Status Date | range | ")
        } else {
            s7 := ";"
            CrPick(MerFind(GetBravoRoot(), {AutomationId: "BoxSelectCriteria"}), ["Web Platform"], &s7)
            wpc := GoInvCriteriaValues("Web Platform", &out)
            wpOk := false
            if wpc {
                s8 := ";"
                got := CrPick(wpc, ["eBay", "EBAY", "Ebay", "eBay Auction"], &s8)
                wv := ""
                try wv := CrAfter("Web Platform", "BravoComboBox").Value
                out .= "web platform picked='" . got . "' value='" . wv . "'`r`n"
                wpOk := (got != "")
            }
            extraOk := wpOk
        }
        rows := CrRowTexts()
        out .= "final rows: " . rows . "`r`n"
        lay := MerFind(GetBravoRoot(), {ClassName: "LayoutView"})
        sb := lay ? MerFind(lay, {Name: "Save", Type: "Button"}) : 0
        noUpd := !MerFind(GetBravoRoot(), {Name: "Update", Type: "Button"})
        gate := "name=" . nameOk . " shared=" . sharedOk . " layout=" . layoutOk . " status=" . statusOk . " extra=" . extraOk . " save=" . (sb ? 1 : 0) . " noUpdate=" . noUpd
        out .= "GATE " . gate . "`r`n"
        MerShot(st . "_" . StrLower(tag) . "_1")
        allOk := (nameOk && sharedOk && layoutOk && statusOk && extraOk && sb && noUpd)
        if !allOk
            verdict := "NOSAVE " . gate
        else if !doSave
            verdict := "DRY OK (all checks pass, not saved) " . gate
        else {
            sb.Click("left")
            Sleep(4000)
            MerWaitNotHung(60)
            saved := true
            MerShot(st . "_" . StrLower(tag) . "_2")
            if !MerFind(GetBravoRoot(), {AutomationId: "BoxSelectCriteria"}) {
                DismissPopups()
                cr2 := MerFind(GetBravoRoot(), {Name: "Custom Reports", Type: "Button"})
                if cr2 {
                    cr2.Click("left")
                    Sleep(4000)
                }
            }
            bar := MerFind(GetBravoRoot(), {ClassName: "EntityAdvancedSearchControlBarView"})
            sc := bar ? MerFind(bar, {ClassName: "BravoComboBox"}) : 0
            seen2 := ";"
            have := sc ? CrPick(sc, [name], &seen2, false) : ""
            verdict := (have != "") ? "SAVED+LISTED " . gate : "SAVE CLICKED but not seen in list " . gate
        }
    } catch as e {
        verdict := (saved ? "ERROR AFTER SAVE " : "NOSAVE ") . e.Message
    }
    closed := CrCancelOut(&out)
    MerWrite(outFile, out)
    GoResult(st, tag . " " . verdict . " / dialog " . (closed ? "closed" : "STILL OPEN"))
    try BackToDashboard()
}
