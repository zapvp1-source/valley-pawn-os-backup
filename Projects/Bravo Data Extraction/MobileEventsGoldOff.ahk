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
        else if (MODE = "crprobe")
            GoCrProbe(st)
        else if (MODE = "crcustdry")
            GoCrCustDry(st)
        else if (MODE = "crprobecust")
            GoCrProbe(st, "Customers")
        else if (MODE = "apponly" || MODE = "appauto" || MODE = "apponlyocc" || MODE = "appautoocc") {
            if (STORES.Length != 1) {
                GoResult(st, "APPONLY refused: one store per run")
                continue
            }
            ; ...occ (2026-11-24, Joshua OK on birthday/anniversary): the Birthday and Store Anniversary events instead
            GoAppOnly(st, (MODE = "apponly" || MODE = "apponlyocc") ? "MobilePawn" : "AUTO", InStr(MODE, "occ") ? "occ" : "loan")
            GoVerify(st)
        }
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
GoCrProbe(st, side := "Loans/Buys") {
    global DUMP_COUNT
    el := MerFind(GetBravoRoot(), {Name: side})
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
        if (aid = "BoxSelectCriteria") {
            sx := ";"
            for pp in CrPopups() {
                ll := 0
                try ll := pp.FindElement({ClassName: "ListBox"})
                if !ll
                    continue
                vv := 0
                Loop 12 {
                    for it in ll.GetChildren() {
                        for t in it.FindElements({Type: "Text"}) {
                            nn := ""
                            try nn := t.Name
                            if (nn != "" && !InStr(sx, ";" . nn . ";"))
                                sx .= nn . ";"
                        }
                    }
                    if (vv >= 100)
                        break
                    vv += 10
                    try ll.ScrollPattern.SetScrollPercent(vv)
                    Sleep(400)
                }
            }
            out .= "ALL CRITERIA: " . sx . "`r`n"
        }
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
    MerWrite(OUT_DIR . "\" . st . ((side = "Loans/Buys") ? "_crprobe.txt" : "_crprobe_cust.txt"), out)
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
; apponly (2026-11-21, Joshua: "lets do the culpeper cut over"). ONE store per run. Sets the delivery choice of the
; three reminder events Chekkit now texts - Loan Courtesy Reminder, Layaway Notice, Loan Past Due (Due Date) - from
; AUTO to MobilePawn (app notice only), so no customer is texted by both systems. Nothing else is touched. Presses Ok
; only if all three changed to the same non-text setting; otherwise Cancel. "appauto" puts the same three back to AUTO.
; ============================================================================
GoAppOnly(st, want, which := "loan") {
    if !MerOpenEditor() {
        GoResult(st, "APPONLY editor did not open")
        try BackToDashboard()
        return
    }
    pane := MerFind(GetBravoRoot(), {ClassName: "ScrollViewer"})
    std := Map("Loan Courtesy Reminder",1, "Layaway Notice",1, "Loan Past Due (Due Date)",1)
    if (which = "occ")
        std := Map("Birthday",1, "Store Anniversary",1)
    title := "", changed := 0, failed := 0, already := 0, log := "", codes := Map()
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
            if (want = "MobilePawn" && v != "NTFAUT" && v != "NTFSMS") {
                already += 1
                codes[v] := 1
                log .= " " . title . ":already(" . v . ")"
            } else if (want = "AUTO" && v = "NTFAUT") {
                already += 1
                log .= " " . title . ":already(AUTO)"
            } else {
                ok := false, v2 := ""
                Loop 3 {
                    GoBringIntoView(pane, k)
                    Sleep(1000)
                    ok := GoPick(k, want)
                    v2 := ""
                    try v2 := k.Value
                    if (ok && v2 != v && v2 != "")
                        break
                    Sleep(1500)
                }
                good := (want = "AUTO") ? (v2 = "NTFAUT") : (v2 != "" && v2 != "NTFAUT" && v2 != "NTFSMS")
                if (ok && good) {
                    changed += 1
                    codes[v2] := 1
                    log .= " " . title . ":" . v . "->" . v2
                } else {
                    failed += 1
                    log .= " " . title . ":FAILED(" . v2 . ")"
                }
            }
            std.Delete(title)
        }
    }
    line := "APPONLY want=" . want . " changed=" . changed . " already=" . already . " failed=" . failed . " notfound=" . std.Count . log
    if (changed > 0 && failed = 0 && std.Count = 0 && codes.Count <= 1) {
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

; crcustdry (2026-11-22): LOOK ONLY. Customers > Custom Reports > New Report, add Birthday and First Time In,
; record each row and its operator choices, list saved reports and layouts, leave by Cancel. Never Save.
GoCrCustDry(st) {
    global DUMP_COUNT
    out := ""
    el := MerFind(GetBravoRoot(), {Name: "Customers"})
    if !el {
        GoResult(st, "CRCUSTDRY Customers not found")
        return
    }
    el.Click("left")
    Sleep(5000)
    DismissPopups()
    MerWaitNotHung(90)
    cr := MerFind(GetBravoRoot(), {Name: "Custom Reports", Type: "Button"})
    if !cr {
        GoResult(st, "CRCUSTDRY Custom Reports button not found")
        try BackToDashboard()
        return
    }
    cr.Click("left")
    Sleep(4000)
    MerWaitNotHung(60)
    if !MerFind(GetBravoRoot(), {AutomationId: "BoxSelectCriteria"}) {
        GoResult(st, "CRCUSTDRY dialog did not open")
        try BackToDashboard()
        return
    }
    try {
        bar := MerFind(GetBravoRoot(), {ClassName: "EntityAdvancedSearchControlBarView"})
        sc := bar ? MerFind(bar, {ClassName: "BravoComboBox"}) : 0
        seen := ";"
        if sc
            Loop 3 {
                CrPick(sc, ["<none>"], &seen, false)
                if (StrLen(seen) >= 20)
                    break
                Sleep(2000)
            }
        out .= "saved reports: " . seen . "`r`n"
        nr := MerFind(GetBravoRoot(), {Name: "New Report", Type: "Button"})
        nr.Click("left")
        Sleep(2500)
        s2 := ";"
        CrPick(MerFind(GetBravoRoot(), {AutomationId: "BoxColumns"}), ["<none>"], &s2, false)
        out .= "layouts: " . s2 . "`r`n"
        for crit in ["Birthday", "First Time In"] {
            sx := ";"
            got := CrPick(MerFind(GetBravoRoot(), {AutomationId: "BoxSelectCriteria"}), [crit], &sx)
            Sleep(800)
            out .= "after adding " . crit . " (picked '" . got . "'): " . CrRowTexts() . "`r`n"
            lv := CrList()
            op := 0, hit := false
            for k in lv.GetChildren() {
                c := "", n := ""
                try c := k.ClassName
                try n := k.Name
                if (!hit) {
                    if (c = "TextBlock" && n = crit)
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
                CrDumpPopups(&out, "operators for " . crit)
                if (CrPopups().Length > 0) {
                    Send("{Escape}")
                    Sleep(900)
                }
            }
        }
        out .= "## criteria area`r`n"
        DUMP_COUNT := 0
        try MerDump(GetBravoRoot().FindElement({ClassName: "FilterEditingView"}), 0, &out)
    } catch as e {
        out .= "ERROR " . e.Message . "`r`n"
    }
    closed := CrCancelOut(&out)
    MerWrite(OUT_DIR . "\" . st . "_crcustdry.txt", out)
    GoResult(st, "CRCUSTDRY done / dialog " . (closed ? "closed (nothing saved)" : "STILL OPEN"))
    try BackToDashboard()
}
