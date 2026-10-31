#Requires AutoHotkey v2.0
#SingleInstance Force
; _lock_probe.ahk — inspect: where is "Lock Session" in Bravo 2026.10.0.85 and what does clicking it open. 2026-10-30.
global WN_LOGFILE := A_ScriptDir . "\logs\_lock_probe2.log"
L(m) {
    global WN_LOGFILE
    FileAppend(FormatTime(, "yyyy-MM-dd HH:mm:ss") . " " . m . "`n", WN_LOGFILE)
}
#Include %A_ScriptDir%\lib\UIA-v2\UIA.ahk
L("=== start")
Main()
L("=== end")
ExitApp()
Dump(el, tag) {
    try {
        for c in el.FindAll(UIA.TrueCondition) {
            n := "", id := "", t := "", r := ""
            try n := c.Name
            try id := c.AutomationId
            try t := c.LocalizedType
            try {
                rr := c.BoundingRectangle
                r := rr.l . "," . rr.t . "," . rr.r . "," . rr.b
            }
            if (n != "" || id != "")
                L(tag . " [" . t . "] name=[" . SubStr(n, 1, 80) . "] id=[" . id . "] rect=" . r)
        }
    }
}
Main() {
    hwnd := WinExist("Bravo ")
    if !hwnd {
        L("no Bravo window")
        return
    }
    root := UIA.ElementFromHandle(hwnd)
    L("v2 probe — window " . WinGetTitle("ahk_id " . hwnd))
    hl := 0
    try hl := root.FindElement({Name: "Lock Session", Type: "Hyperlink"})
    if !hl {
        L("Lock Session HYPERLINK not found")
        return
    }
    rr := hl.BoundingRectangle
    L("hyperlink rect=" . rr.l . "," . rr.t . "," . rr.r . "," . rr.b)
    try L("invoke available=" . hl.IsInvokePatternAvailable)
    ok := false
    try {
        hl.InvokePattern.Invoke()
        ok := true
        L("Invoke() returned")
    } catch as e {
        L("Invoke failed: " . e.Message)
    }
    if !ok {
        try {
            hl.Click("left")
            L("mouse click sent")
        } catch as e {
            L("mouse click failed: " . e.Message)
        }
    }
    Sleep(6000)
    L("--- after")
    for nm in ["Global Access", "Resume Session", "End Session", "Cancel", "Continue", "Back", "Username", "Password", "Login", "Log In", "Unlock", "Select", "Store", "What's New in Bravo", "Close"] {
        f := 0
        try f := root.FindElement({Name: nm})
        if f {
            b := f.BoundingRectangle
            L("FOUND [" . nm . "] type=" . f.LocalizedType . " rect=" . b.l . "," . b.t . "," . b.r . "," . b.b)
        }
    }
    for h in WinGetList() {
        try {
            t := WinGetTitle("ahk_id " . h)
            if (t != "")
                L("WIN " . WinGetClass("ahk_id " . h) . " | " . t)
        }
    }
    cnt := 0
    try {
        for c in root.FindAll(UIA.TrueCondition) {
            n := ""
            try n := c.Name
            if (n = "")
                continue
            t := ""
            try t := c.LocalizedType
            if !(t = "button" || t = "hyperlink" || t = "tab item" || t = "menu item" || t = "list item")
                continue
            b := c.BoundingRectangle
            L("EL [" . t . "] " . SubStr(n, 1, 70) . " rect=" . b.l . "," . b.t)
            cnt += 1
            if (cnt > 120)
                break
        }
    }
}
