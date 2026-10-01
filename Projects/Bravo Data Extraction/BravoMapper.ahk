; ============================================================================
; BravoMapper.ahk  -- STANDALONE, READ-ONLY map of every Bravo screen + report.
; Added 2026-09-30 (Joshua: "map ALL of Bravo overnight").
;
; ADDITIVE: new file. Does NOT touch bravo_watcher.ahk, any report handler,
; any saved Ad Hoc report, or the trigger queue. Reuses lib\ helpers only.
;
; What it does, per step (checkpointed, resumable across nights):
;   D_*  dashboard dump
;   M_*  open each right-sidebar module, dump the full UIA tree + screenshot,
;        record every clickable control it offers (cand_*.txt)
;   R_*  Reports tree: expand every category, dump; then open each report's
;        parameter dialog (double-click), dump it, Cancel out (never runs Ok)
;   T_*  dashboard task tiles (list views only)
;   S_*  level-2: click each SAFE control found in a module (tabs, filters,
;        lookups, Custom Reports) and dump what it opens; Custom Reports
;        dialogs also get their criteria / columns / saved-report lists.
;
; SAFETY (hard rules, not options):
;   - Never clicks Ok/Save/Post/Void/Pay/etc. (DENY regex below).
;   - Never opens Close Store / Open Till / Transfer Tender.
;   - Returns to Dashboard after EVERY step (lib BackToDashboard, which only
;     ever Cancels / answers Yes to "abandon changes").
;   - Yields while the pipeline has a pending/just-claimed trigger.
;   - Stops at DEADLINE (arg1, yyyyMMddHHmmss) and leaves Bravo on Dashboard.
;   - If Bravo stops responding: writes ABORT hung and exits (Mac wrapper
;     runs the health gate).
;
; Args: <deadline yyyyMMddHHmmss> <mode full|smoke> <recoveryStore CUL>
; Output: output\bravo_map\  (screens\*.txt, shots\*.png, index.tsv,
;         _done.txt, _fail.txt, _status.txt, cand_*.txt, lists\*.txt)
; ASCII only (the AHK parser has choked on non-ASCII comments before).
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

global MAP_DIR     := A_ScriptDir . "\output\bravo_map"
global SCR_DIR     := MAP_DIR . "\screens"
global SHOT_DIR    := MAP_DIR . "\shots"
global LIST_DIR    := MAP_DIR . "\lists"
global DONE_FILE   := MAP_DIR . "\_done.txt"
global FAIL_FILE   := MAP_DIR . "\_fail.txt"
global STATUS_FILE := MAP_DIR . "\_status.txt"
global INDEX_FILE  := MAP_DIR . "\index.tsv"

global DEADLINE  := (A_Args.Length >= 1) ? A_Args[1] : FormatTime(DateAdd(A_Now, 20, "Minutes"), "yyyyMMddHHmmss")
global MODE      := (A_Args.Length >= 2) ? A_Args[2] : "smoke"
global RSTORE    := (A_Args.Length >= 3) ? A_Args[3] : "CUL"
global SMOKE_MAX := 3

global DONE := Map()
global FAILS := Map()
global STEPS_RUN := 0
global DUMP_COUNT := 0
global BASELINE := Map()

; Words that mean "this control changes data / leaves the app". Never clicked.
global DENY_RX := "i)(^|\W)(new|add|create|save|post|posting|void|delete|remove|close|open till|transfer|pay|redeem|renew|extend|forfeit|sell|fast sale|buy|pawn|receive|print|send|settle|refund|return|adjust|retag|price|export|import|submit|approve|complete|finali[sz]e|process|apply|confirm|yes|ok|done|merge|lock|logout|log out|end session|email|text|sms|scan|upload|charge|tender|deposit|payout|paid out|split|issue|reprint|ship|label|publish|sync|update|edit|reset|clear|cancel|minimize|maximize|restore|chat|plugins|webballs|solution center|support inbox|menu|expire now|release|reverse|restock|write off|scrap|melt|batch|intake|check in|check out|clock|till|safe|drawer|approve|authorize|finger|photo|camera|signature|sign)(\W|$)"

; Right-sidebar modules to open (label, AutomationId suffix). Close Store,
; Open Till and Transfer Tender are deliberately absent.
global MODULES := [
    ["Inventory", "Inventory"],
    ["Loans/Buys", "LoansBuys"],
    ["Layaways", "Layaways"],
    ["Customers", "Customers"],
    ["Void/View Transactions", "VoidViewTransactions"],
    ["eCommerce", "eCommerce"],
    ["Web Auctions", "WebAuctions"],
    ["eBay Listings", "eBayListings"],
    ["Lost or Damaged Items", "LostOrDamagedItems"],
    ["System Configuration", "SystemConfiguration"],
    ["Transactions", "Transactions"]
]
; Dashboard task tiles that only open a filtered list.
global TILES := ["Locate Layaways", "Layaways Overdue", "Locate Loan/Buy", "Loans To Expire",
                 "Locate Pending Payment", "Web Fulfillment", "Web In-Store Pickup", "Web Offers", "Web Feedbacks"]

OnError(MapperOnError)
Main()
ExitApp(0)

; ---------------------------------------------------------------------------
Main() {
    global
    for d in [MAP_DIR, SCR_DIR, SHOT_DIR, LIST_DIR] {
        if !DirExist(d)
            DirCreate(d)
    }
    InitLog(A_ScriptDir . "\logs", "bravomap-" . FormatTime(, "yyyy-MM-ddTHH-mm-ss"))
    LogMessage("BravoMapper mode=" . MODE . " deadline=" . DEADLINE . " recoveryStore=" . RSTORE)
    LoadSet(DONE_FILE, DONE, false)
    LoadSet(FAIL_FILE, FAILS, true)
    SetStatus("STARTING")

    if !EnsureBravoDashboard(BRAVO_PASSWORD, RSTORE) {
        SetStatus("ABORT no-dashboard-at-start")
        ExitApp(2)
    }
    if !GoDash() {
        SetStatus("ABORT no-dashboard-at-start")
        ExitApp(2)
    }
    BuildBaseline()

    ; ---- Phase 1: dashboard + every module (level 1)
    RunStep("D_dashboard", () => DumpScreen("D_dashboard", "Dashboard"))
    for m in MODULES
        RunStep("M_" . Slug(m[1]), StepModule.Bind(m[1], m[2]))

    ; ---- Phase 2: Reports tree + every report's parameter dialog
    RunStep("R__tree", StepReportTree)
    for rep in ReadLines(LIST_DIR . "\reports.txt")
        RunStep("R_" . Slug(rep), StepReport.Bind(rep))

    ; ---- Phase 3: dashboard tiles
    for t in TILES
        RunStep("T_" . Slug(t), StepTile.Bind(t))

    ; ---- Phase 4: level-2 controls inside each module
    for m in MODULES {
        cf := MAP_DIR . "\cand_" . Slug(m[1]) . ".txt"
        for line in ReadLines(cf) {
            p := StrSplit(line, "`t")
            if (p.Length < 2)
                continue
            RunStep("S_" . Slug(m[1]) . "__" . Slug(p[2]), StepSub.Bind(m[1], m[2], p[1], p[2]))
        }
    }
    Finish("COMPLETE")
}

; ---------------------------------------------------------------------------
; Step bodies
StepModule(label, aid) {
    OpenModule(aid)
    key := "M_" . Slug(label)
    DumpScreen(key, "Module: " . label)
    ; record the new controls this view offers (minus the dashboard baseline)
    out := ""
    skipped := ""
    n := 0
    for c in CollectClickables() {
        k := c["type"] . "|" . c["name"]
        if BASELINE.Has(k)
            continue
        navTypes := (aid = "SystemConfiguration") ? "|TabItem|TreeItem|" : "|Button|Hyperlink|TabItem|TreeItem|MenuItem|SplitButton|"
        if RegExMatch(c["name"], DENY_RX) || InStr(c["name"], "ZTI.") || !InStr(navTypes, "|" . c["type"] . "|") {
            skipped .= c["type"] . "`t" . c["name"] . "`t" . c["aid"] . "`r`n"
            continue
        }
        n += 1
        if (n > 40)
            break
        out .= c["type"] . "`t" . c["name"] . "`t" . c["aid"] . "`r`n"
    }
    WriteFile(MAP_DIR . "\cand_" . Slug(label) . ".txt", out)
    WriteFile(LIST_DIR . "\notclicked_" . Slug(label) . ".txt", skipped)
    LogMessage("   module " . label . ": " . n . " safe controls queued")
    return true
}

StepSub(label, aid, ctype, cname) {
    OpenModule(aid)
    el := FindIn(GetBravoRoot(), {Name: cname, Type: ctype})
    if !el
        el := FindIn(GetBravoRoot(), {Name: cname})
    if !el
        throw Error("control not found: " . cname)
    try el.ScrollItemPattern.ScrollIntoView()
    el.Click("left")
    Sleep(3500)
    DismissPopups()
    WaitNotHung(90)
    key := "S_" . Slug(label) . "__" . Slug(cname)
    if (cname = "Custom Reports")
        return DumpCustomReports(key, label)
    DumpScreen(key, label . " > " . cname)
    return true
}

StepTile(name) {
    el := FindIn(GetBravoRoot(), {Name: name})
    if !el
        throw Error("tile not found: " . name)
    el.Click("left")
    Sleep(4000)
    DismissPopups()
    WaitNotHung(90)
    DumpScreen("T_" . Slug(name), "Dashboard tile: " . name)
    return true
}

StepReportTree() {
    OpenReports()
    DumpScreen("R__tree", "Reports tree (all categories expanded)")
    out := ""
    cats := ""
    for el in FindAllIn(GetBravoRoot(), "TreeItem") {
        nm := "", aid := ""
        try nm := el.Name
        try aid := el.AutomationId
        if (nm = "" || !InStr(aid, "ReportTree"))
            continue
        kids := 0
        try kids := el.FindElements({Type: "TreeItem"}).Length
        if (kids > 0)
            cats .= nm . "`t" . aid . "`r`n"
        else
            out .= nm . "`r`n"
    }
    WriteFile(LIST_DIR . "\report_categories.txt", cats)
    WriteFile(LIST_DIR . "\reports.txt", out)
    return (out != "")
}

StepReport(name) {
    OpenReports()
    el := FindIn(GetBravoRoot(), {Name: name, Type: "TreeItem"})
    if !el
        throw Error("report item not found: " . name)
    try el.ScrollItemPattern.ScrollIntoView()
    Sleep(500)
    el.Click("left", 2)          ; opens the parameter dialog (or a preview)
    Sleep(5000)
    DismissPopups()
    WaitNotHung(120)
    DumpScreen("R_" . Slug(name), "Report: " . name)
    return true
}

; Custom Reports editor: dump dialog + criteria / columns / saved-report lists,
; then leave via the named Cancel (never Done -- Done loops in this editor).
DumpCustomReports(key, label) {
    DumpScreen(key, label . " > Custom Reports")
    for aid in ["BoxSelectCriteria", "BoxColumns"] {
        names := ComboItems({AutomationId: aid})
        WriteFile(LIST_DIR . "\" . key . "_" . aid . ".txt", Join(names, "`r`n"))
    }
    saved := SavedReportCombo()
    if saved {
        names := ComboItems(0, saved)
        WriteFile(LIST_DIR . "\" . key . "_SavedReports.txt", Join(names, "`r`n"))
    }
    Loop 2 {
        try ClickByName("Cancel", 3000)
        Sleep(1200)
        DismissPopups()
    }
    return true
}

; ---------------------------------------------------------------------------
; Navigation helpers
OpenModule(aidSuffix) {
    el := FindIn(GetBravoRoot(), {AutomationId: "Dashboard.Buttons." . aidSuffix})
    if !el
        throw Error("sidebar item not found: " . aidSuffix)
    el.Click("left")
    Sleep(4000)
    DismissPopups()
    WaitNotHung(90)
    return true
}

OpenReports() {
    OpenModule("Reports")
    Sleep(1500)
    ; expand every report category (two passes: nested categories)
    Loop 2 {
        for el in FindAllIn(GetBravoRoot(), "TreeItem") {
            aid := ""
            try aid := el.AutomationId
            if !InStr(aid, "ReportTree")
                continue
            try {
                p := el.ExpandCollapsePattern
                if (p.ExpandCollapseState = 0)
                    p.Expand()
            }
        }
        Sleep(1200)
    }
}

GoDash() {
    ok := false
    try ok := BackToDashboard()
    if ok
        return true
    LogMessage("   GoDash: BackToDashboard failed - EnsureBravoDashboard")
    ok := false
    try ok := EnsureBravoDashboard(BRAVO_PASSWORD, RSTORE)
    return ok && ExistsByName("Reports")
}

; ---------------------------------------------------------------------------
; Step runner / control
RunStep(key, fn) {
    global DONE, FAILS, STEPS_RUN, MODE, SMOKE_MAX
    if DONE.Has(key)
        return
    if (FAILS.Has(key) && FAILS[key] >= 2)
        return
    CheckDeadline()
    WaitIfPipelineBusy()
    SetStatus("RUNNING " . key)
    LogMessage(">> step " . key)
    ok := false
    try {
        ok := fn.Call()
    } catch as e {
        LogMessage("   step error: " . e.Message)
        ok := false
    }
    if IsHung() {
        WaitNotHung(120)
        if IsHung() {
            SetStatus("ABORT hung after " . key)
            ExitApp(4)
        }
    }
    if ok {
        DONE[key] := 1
        AppendLine(DONE_FILE, key)
    } else {
        FAILS[key] := (FAILS.Has(key) ? FAILS[key] : 0) + 1
        AppendLine(FAIL_FILE, key)
        try DumpScreen("ERR_" . key, "state after failed step")
    }
    STEPS_RUN += 1
    if !GoDash() {
        SetStatus("ABORT no-dashboard after " . key)
        ExitApp(2)
    }
    if (MODE = "smoke" && STEPS_RUN >= SMOKE_MAX)
        Finish("DONE-SMOKE")
}

CheckDeadline() {
    global DEADLINE
    if (A_Now >= DEADLINE)
        Finish("PAUSED-DEADLINE")
}

Finish(s) {
    GoDash()
    SetStatus(s)
    LogMessage("=== BravoMapper finished: " . s . " ===")
    ExitApp(0)
}

; Yield to the real pipeline: a trigger waiting in triggers\ (fresh) or one
; claimed in the last 3 minutes means the watcher is (about to be) driving Bravo.
WaitIfPipelineBusy() {
    first := true
    Loop {
        why := PipelineBusy()
        if (why = "")
            return
        if first {
            LogMessage("   yielding to pipeline: " . why)
            GoDash()
            first := false
        }
        SetStatus("YIELD " . why)
        CheckDeadline()
        Sleep(60000)
    }
}

PipelineBusy() {
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

IsHung() {
    h := WinExist(BRAVO_WIN_TITLE)
    if !h
        return false
    return DllCall("IsHungAppWindow", "ptr", h, "int")
}

WaitNotHung(sec) {
    t0 := A_TickCount
    while IsHung() {
        if (A_TickCount - t0 > sec * 1000)
            return false
        Sleep(3000)
    }
    return true
}

MapperOnError(e, mode) {
    try LogMessage("UNHANDLED: " . e.Message . " line " . e.Line)
    try SetStatus("ABORT unhandled " . e.Message)
    ExitApp(3)
    return 1
}

; ---------------------------------------------------------------------------
; UIA helpers
FindIn(root, cond) {
    el := 0
    try el := root.FindElement(cond)
    return el
}

FindAllIn(root, typ) {
    els := []
    try els := root.FindElements({Type: typ})
    return els
}

CollectClickables() {
    res := []
    seen := Map()
    root := GetBravoRoot()
    for t in ["Button", "Hyperlink", "TabItem", "RadioButton", "TreeItem", "MenuItem", "SplitButton", "CheckBox"] {
        for el in FindAllIn(root, t) {
            n := "", a := ""
            try n := el.Name
            try a := el.AutomationId
            k := t . "|" . n
            if (n = "" || seen.Has(k))
                continue
            seen[k] := 1
            res.Push(Map("type", t, "name", n, "aid", a))
        }
    }
    return res
}

BuildBaseline() {
    global BASELINE
    for c in CollectClickables()
        BASELINE[c["type"] . "|" . c["name"]] := 1
    LogMessage("   dashboard baseline controls: " . BASELINE.Count)
}

; Open a combo, harvest every list entry (scrolling until stable), close it.
ComboItems(cond, combo := 0) {
    out := []
    seen := Map()
    if !combo
        combo := FindIn(GetBravoRoot(), cond)
    if !combo
        return out
    before := Map()
    for el in AllBravoItems()
        before[el] := 1
    try combo.Click("left")
    Sleep(1500)
    stable := 0
    Loop 60 {
        added := 0
        for nm in AllBravoItems() {
            if (nm = "" || seen.Has(nm) || before.Has(nm))
                continue
            seen[nm] := 1
            out.Push(nm)
            added += 1
        }
        stable := added ? 0 : stable + 1
        if (stable >= 4)
            break
        Send("{PgDn}")
        Sleep(500)
    }
    Send("{Escape}")
    Sleep(800)
    return out
}

; Names (or child-text labels) of list/data/tree items across all Bravo windows.
AllBravoItems() {
    names := []
    for hwnd in WinGetList("ahk_exe Bravo.exe") {
        root := 0
        try root := UIA.ElementFromHandle(hwnd)
        if !root
            continue
        for typ in ["ListItem", "DataItem"] {
            for el in FindAllIn(root, typ) {
                nm := "", lbl := ""
                try nm := el.Name
                try {
                    for t in el.FindElements({Type: "Text"}) {
                        tn := ""
                        try tn := t.Name
                        if (tn != "")
                            lbl .= (lbl = "" ? "" : " | ") . tn
                    }
                }
                names.Push(lbl != "" ? lbl : nm)
            }
        }
    }
    return names
}

; Bottom-most "BravoComboBox" edit that is not criteria/columns/shared.
SavedReportCombo() {
    best := 0, bestTop := -1
    for el in FindAllIn(GetBravoRoot(), "Edit") {
        n := "", a := ""
        try n := el.Name
        try a := el.AutomationId
        if (n != "BravoComboBox" || a = "BoxColumns" || a = "BoxIsShared" || a = "BoxSelectCriteria")
            continue
        top := 0
        try top := el.BoundingRectangle.t
        if (top > bestTop) {
            best := el
            bestTop := top
        }
    }
    return best
}

; ---------------------------------------------------------------------------
; Dump + screenshot
DumpScreen(key, note := "") {
    global DUMP_COUNT
    file := SCR_DIR . "\" . key . ".txt"
    title := ""
    try title := WinGetTitle(BRAVO_WIN_TITLE)
    out := "# key: " . key . "`r`n# captured: " . FormatTime(, "yyyy-MM-dd HH:mm:ss") . "`r`n# title: " . title . "`r`n# note: " . note . "`r`n"
    out .= "# format: [type] N=name | A=automationId | C=class | E/- enabled | off=offscreen | R=l,t,r,b | V=value`r`n"
    mainHwnd := WinExist(BRAVO_WIN_TITLE)
    DUMP_COUNT := 0
    try {
        DumpElem(GetBravoRoot(), 0, &out)
    } catch as e {
        out .= "ERROR main window: " . e.Message . "`r`n"
    }
    for hwnd in WinGetList("ahk_exe Bravo.exe") {
        if (hwnd = mainHwnd)
            continue
        if !DllCall("IsWindowVisible", "ptr", hwnd, "int")
            continue
        wt := "", wc := ""
        try wt := WinGetTitle(hwnd)
        try wc := WinGetClass(hwnd)
        out .= "`r`n## extra window hwnd=" . hwnd . " title=" . wt . " class=" . wc . "`r`n"
        DUMP_COUNT := 0
        try DumpElem(UIA.ElementFromHandle(hwnd), 0, &out)
    }
    WriteFile(file, out)
    Shot(key)
    AppendLine(INDEX_FILE, key . "`t" . note . "`t" . FormatTime(, "yyyy-MM-dd HH:mm:ss") . "`t" . title)
    return true
}

DumpElem(el, depth, &out) {
    global DUMP_COUNT
    if (depth > 30 || DUMP_COUNT > 6000)
        return
    DUMP_COUNT += 1
    t := "", n := "", a := "", c := "", en := "?", off := "", rs := "", v := ""
    try t := el.LocalizedType
    try n := el.Name
    try a := el.AutomationId
    try c := el.ClassName
    try en := el.IsEnabled ? "E" : "-"
    try off := el.IsOffscreen ? " off" : ""
    try {
        r := el.BoundingRectangle
        rs := r.l . "," . r.t . "," . r.r . "," . r.b
    }
    try v := el.Value
    ind := ""
    Loop depth
        ind .= "  "
    line := ind . "[" . t . "] N=" . Clean(n) . " | A=" . Clean(a) . " | C=" . Clean(c) . " | " . en . off . " | R=" . rs
    if (v != "")
        line .= " | V=" . Clean(v)
    out .= line . "`r`n"
    kids := []
    try kids := el.GetChildren()
    total := kids.Length
    i := 0
    for k in kids {
        i += 1
        if (i > 80) {
            out .= ind . "  ... +" . (total - 80) . " more children not dumped`r`n"
            break
        }
        DumpElem(k, depth + 1, &out)
    }
}

Shot(key) {
    pngEsc := StrReplace(SHOT_DIR . "\" . key . ".png", "'", "''")
    cmd := "powershell -NoProfile -WindowStyle Hidden -Command `"Add-Type -AssemblyName System.Windows.Forms; Add-Type -AssemblyName System.Drawing; $b = New-Object System.Drawing.Bitmap([System.Windows.Forms.SystemInformation]::VirtualScreen.Width, [System.Windows.Forms.SystemInformation]::VirtualScreen.Height); $g = [System.Drawing.Graphics]::FromImage($b); $g.CopyFromScreen([System.Windows.Forms.SystemInformation]::VirtualScreen.Location, [System.Drawing.Point]::Empty, $b.Size); $b.Save('" . pngEsc . "', 'Png'); $g.Dispose(); $b.Dispose()`""
    try RunWait(cmd, , "Hide")
}

; ---------------------------------------------------------------------------
; Small utilities
Slug(s) {
    s := RegExReplace(s, "[^A-Za-z0-9]+", "_")
    s := Trim(s, "_")
    return SubStr(s, 1, 60)
}

Clean(s) {
    s := String(s)
    s := StrReplace(s, "`r", " ")
    s := StrReplace(s, "`n", " ")
    s := StrReplace(s, "`t", " ")
    s := StrReplace(s, "|", "/")
    return SubStr(s, 1, 160)
}

Join(arr, sep) {
    s := ""
    for x in arr
        s .= (A_Index = 1 ? "" : sep) . x
    return s
}

ReadLines(path) {
    arr := []
    if !FileExist(path)
        return arr
    Loop Read, path {
        l := Trim(A_LoopReadLine)
        if (l != "")
            arr.Push(l)
    }
    return arr
}

LoadSet(path, m, counting) {
    for l in ReadLines(path)
        m[l] := counting ? (m.Has(l) ? m[l] + 1 : 1) : 1
}

WriteFile(path, text) {
    try FileDelete(path)
    FileAppend(text, path, "UTF-8-RAW")
}

AppendLine(path, text) {
    FileAppend(text . "`r`n", path, "UTF-8-RAW")
}

SetStatus(s) {
    try FileDelete(STATUS_FILE)
    try FileAppend(FormatTime(, "yyyy-MM-dd HH:mm:ss") . " " . s, STATUS_FILE, "UTF-8-RAW")
}
