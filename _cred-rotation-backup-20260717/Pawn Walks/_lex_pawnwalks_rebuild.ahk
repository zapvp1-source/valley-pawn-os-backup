; Rebuild "Claude Pawn Walks" at LEX (Joshua-approved 2026-06-12):
;   1. load the saved report (Enter-commit workaround)
;   2. BoxColumns  -> select layout 'Pawn Walk' (the shared 4-column layout)
;   3. BoxSelectCriteria -> add 'Transaction Date', operator Between, dates 6/11/2026
;   4. SANITY GATE: only click the dialog Save button if the criteria row and
;      layout actually took; otherwise Cancel and save nothing.
; Result: logs\_lexpw_rebuild_result.txt = SAVED / NOSAVE <reason> / FAIL <reason>
#Requires AutoHotkey v2.0
#SingleInstance Off
#Include lib\Json.ahk
#Include lib\Bravo.ahk
#Include lib\StoreCycle.ahk

global CONFIG := Map()
CONFIG["paths.logs"]     := A_ScriptDir . "\logs"
CONFIG["bravo.username"] := "FREE1@WAY"
CONFIG["bravo.password"] := "Health2035!"

global RES := CONFIG["paths.logs"] . "\_lexpw_rebuild_result.txt"
WriteRes(s) {
    global RES
    try FileDelete(RES)
    try FileAppend(s, RES, "UTF-8")
}

InitLog(CONFIG["paths.logs"], "lexpw-rebuild-" . FormatTime(, "yyyyMMdd-HHmmss"))
LogMessage("=== LEX PawnWalks REBUILD start ===")
WriteRes("RUNNING")

ActivateBravo()
Sleep(800)
if !EnsureStore("LEX", CONFIG["bravo.password"]) {
    WriteRes("FAIL EnsureStore")
    ExitApp(1)
}
DismissPopups()
try {
    ClickByName("Loans/Buys", 8000)
    Sleep(1500)
    DismissPopups()
    ClickByName("Custom Reports", 5000)
    Sleep(1500)
} catch as e {
    WriteRes("FAIL open dialog: " . e.Message)
    ExitApp(1)
}

; --- 1. load Claude Pawn Walks ------------------------------------------------
try {
    c := FindBottomSavedReportCombo()
    if c {
        c.Click("left")
        Sleep(900)
    }
    ClickByName("Claude Pawn Walks", 3000)
    Sleep(900)
    if ExistsByName("<new report>") {
        Send("{Enter}")
        Sleep(1200)
    }
    if ExistsByName("<new report>") {
        WriteRes("FAIL report selection would not commit")
        CleanExit(1)
    }
    LogMessage("step1: report loaded")
    Sleep(800)
} catch as e {
    WriteRes("FAIL select: " . e.Message)
    CleanExit(1)
}

; --- 2. set Columns layout = 'Pawn Walk' ---------------------------------------
layoutOk := false
try {
    colCombo := FindComboByAid("BoxColumns")
    if !colCombo
        throw Error("BoxColumns not found")
    colCombo.Click("left")
    Sleep(1000)
    if !ExistsByName("Pawn Walk")
        throw Error("layout list did not show Pawn Walk")
    ClickByName("Pawn Walk", 3000)
    Sleep(900)
    ; commit check: layout list closed? (its sibling 'Trade In View' gone)
    if ExistsByName("Trade In View") {
        LogMessage("step2: layout list still open - sending Enter")
        Send("{Enter}")
        Sleep(900)
    }
    if ExistsByName("Trade In View")
        throw Error("layout selection would not commit")
    layoutOk := true
    LogMessage("step2: columns layout set to Pawn Walk")
} catch as e {
    LogMessage("step2 FAILED: " . e.Message)
}

; --- 3. add criteria Transaction Date ------------------------------------------
critOk := false
try {
    critCombo := FindComboByAid("BoxSelectCriteria")
    if !critCombo
        throw Error("BoxSelectCriteria not found")
    critCombo.Click("left")
    Sleep(1000)
    found := false
    if ExistsByName("Transaction Date")
        found := true
    ; escalation 1: letter type-ahead (jump to T entries)
    if !found {
        LogMessage("step3: not visible - trying letter type-ahead")
        Loop 8 {
            Send("t")
            Sleep(350)
            if ExistsByName("Transaction Date") {
                found := true
                break
            }
        }
    }
    ; escalation 2: arrow-down scroll
    if !found {
        LogMessage("step3: still not visible - arrow-down scroll")
        Loop 45 {
            Send("{Down}")
            Sleep(160)
            if ExistsByName("Transaction Date") {
                found := true
                break
            }
        }
    }
    ; escalation 3: mouse wheel over the popup list
    if !found {
        LogMessage("step3: still not visible - mouse wheel over popup")
        MouseMove(700, 1000)
        Sleep(300)
        Loop 12 {
            Send("{WheelDown}")
            Sleep(250)
            if ExistsByName("Transaction Date") {
                found := true
                break
            }
        }
    }
    if !found
        throw Error("could not bring Transaction Date into view in criteria list")
    ClickByName("Transaction Date", 3000)
    Sleep(900)
    ; commit check: if the options popup is still open (Enter-commit quirk,
    ; same as the saved-report list on this store), press Enter
    if ExistsByName("Firearm Action") {
        LogMessage("step3: options list still open after click - sending Enter")
        Send("{Enter}")
        Sleep(900)
    }
    ; the option list should be closed now ('Age' option at x~481 gone is hard
    ; to test since Age is also a grid column; instead require a Transaction
    ; Date text to exist in the dialog criteria area)
    Sleep(800)
    if !TextExistsInBox("Transaction Date", 400, 600, 2300, 1700)
        throw Error("no Transaction Date criteria row appeared")
    critOk := true
    LogMessage("step3: Transaction Date criteria row present")
} catch as e {
    LogMessage("step3 FAILED: " . e.Message)
}

; --- 3b. operator -> Between, dates -> 6/11/2026 --------------------------------
betweenOk := false
if critOk {
    try {
        ; operator combo: a BravoComboBox in the criteria area showing '=' or similar;
        ; click the combo nearest right of the Transaction Date label
        opCombo := FindOperatorComboNear("Transaction Date")
        if opCombo {
            opCombo.Click("left")
            Sleep(900)
            for cand in ["Between", "between", "BETWEEN"] {
                if ExistsByName(cand) {
                    ClickByName(cand, 2000)
                    Sleep(900)
                    betweenOk := true
                    LogMessage("step3b: operator set to " . cand)
                    break
                }
            }
            if !betweenOk {
                LogMessage("step3b: no Between option seen - dumping option texts")
                DumpTextsInBox(300, 500, 2400, 2000)
                Send("{Esc}")
                Sleep(600)
            }
        } else {
            LogMessage("step3b: operator combo not found near Transaction Date")
        }
    } catch as e {
        LogMessage("step3b FAILED: " . e.Message)
    }
    ; try to fill the date editors (values get overridden every run anyway)
    LexFillDate(1, "6/11/2026")
    LexFillDate(2, "6/11/2026")
}

LogMessage("--- state before save decision (layoutOk=" . layoutOk . " critOk=" . critOk . " betweenOk=" . betweenOk . ") ---")
DumpTextsInBox(400, 430, 2400, 1700)
DumpEditsAll()

; --- 4. SANITY GATE + SAVE -------------------------------------------------------
if !(layoutOk && critOk) {
    WriteRes("NOSAVE layoutOk=" . layoutOk . " critOk=" . critOk)
    LogMessage("sanity gate failed - cancelling without saving")
    CleanExit(1)
}
saveBtn := FindButtonInBox("Save", 2100, 450, 2450, 700)
if !saveBtn {
    WriteRes("NOSAVE dialog Save button not found in expected region")
    CleanExit(1)
}
try {
    saveBtn.Click("left")
    Sleep(1200)
    LogMessage("step4: clicked dialog Save")
    try DismissPopups()
    Sleep(800)
} catch as e {
    WriteRes("FAIL save click: " . e.Message)
    CleanExit(1)
}
WriteRes("SAVED layoutOk=1 critOk=1 betweenOk=" . betweenOk)
LogMessage("=== REBUILD done: SAVED ===")
CleanExit(0)

; ------------------------------------------------------------------ helpers ---
CleanExit(code) {
    try ClickByName("Cancel", 3000)
    Sleep(800)
    try ClickByName("Cancel", 3000)
    Sleep(800)
    try DismissPopups()
    try BackToDashboard()
    LogMessage("=== exit code " . code . " ===")
    ExitApp(code)
}

FindComboByAid(aid) {
    try {
        root := GetBravoRoot()
        els := root.FindElements({Type: "Edit"})
        for e in els {
            a := ""
            try a := e.AutomationId
            if (a = aid)
                return e
        }
    }
    return 0
}

FindBottomSavedReportCombo() {
    bestElem := 0
    bestY := -1
    try {
        root := GetBravoRoot()
        edits := root.FindElements({Type: "Edit"})
        for e in edits {
            n := ""
            try n := e.Name
            if (n != "BravoComboBox")
                continue
            a := ""
            try a := e.AutomationId
            if (a = "BoxColumns" || a = "BoxIsShared" || a = "BoxSelectCriteria")
                continue
            r := 0
            try r := e.BoundingRectangle
            if !r
                continue
            if (r.t > bestY) {
                bestY := r.t
                bestElem := e
            }
        }
    }
    return bestElem
}

; operator combo = BravoComboBox horizontally right of the Transaction Date
; criteria label, on roughly the same row (+-60px)
FindOperatorComboNear(labelName) {
    lbl := 0
    try {
        root := GetBravoRoot()
        txts := root.FindElements({Type: "Text"})
        for t in txts {
            n := ""
            try n := t.Name
            if (n != labelName)
                continue
            r := 0
            try r := t.BoundingRectangle
            if !r
                continue
            if (r.t > 600 && r.t < 1700 && r.l > 400 && r.l < 1200) {
                lbl := r
                break
            }
        }
        if !lbl
            return 0
        edits := root.FindElements({Type: "Edit"})
        best := 0
        bestX := 99999
        for e in edits {
            n := ""
            try n := e.Name
            if (n != "BravoComboBox")
                continue
            r := 0
            try r := e.BoundingRectangle
            if !r
                continue
            if (Abs(r.t - lbl.t) > 60)
                continue
            if (r.l <= lbl.l)
                continue
            if (r.l < bestX) {
                bestX := r.l
                best := e
            }
        }
        return best
    }
    return 0
}

FindButtonInBox(name, x1, y1, x2, y2) {
    try {
        root := GetBravoRoot()
        btns := root.FindElements({Type: "Button"})
        for b in btns {
            n := ""
            try n := b.Name
            if (n != name)
                continue
            r := 0
            try r := b.BoundingRectangle
            if !r
                continue
            if (r.l >= x1 && r.l <= x2 && r.t >= y1 && r.t <= y2)
                return b
        }
    }
    return 0
}

TextExistsInBox(name, x1, y1, x2, y2) {
    try {
        root := GetBravoRoot()
        txts := root.FindElements({Type: "Text"})
        for t in txts {
            n := ""
            try n := t.Name
            if (n != name)
                continue
            r := 0
            try r := t.BoundingRectangle
            if !r
                continue
            if (r.l >= x1 && r.l <= x2 && r.t >= y1 && r.t <= y2)
                return true
        }
    }
    return false
}

DumpTextsInBox(x1, y1, x2, y2) {
    try {
        root := GetBravoRoot()
        els := root.FindElements({Type: "Text"})
        cnt := 0
        for e in els {
            n := ""
            try n := e.Name
            if (n = "")
                continue
            r := 0
            try r := e.BoundingRectangle
            if !r
                continue
            if (r.l < x1 || r.l > x2 || r.t < y1 || r.t > y2)
                continue
            cnt++
            if (cnt > 120)
                break
            LogMessage("[t] " . Chr(39) . n . Chr(39) . " @" . r.l . "," . r.t)
        }
    }
}

; Fill the Nth BravoDateEdit (sorted by x) with a m/d/yyyy value. Skips with a
; log line if the editor is absent (the daily handler overrides dates anyway).
LexFillDate(position, mdY) {
    wrappers := []
    try {
        root := GetBravoRoot()
        edits := root.FindElements({Type: "Edit"})
        for e in edits {
            n := ""
            try n := e.Name
            if (n != "BravoDateEdit")
                continue
            a := ""
            try a := e.AutomationId
            if (a = "PART_Editor")
                continue
            r := 0
            try r := e.BoundingRectangle
            if !r
                continue
            wrappers.Push(Map("elem", e, "x", r.l))
        }
    }
    if (wrappers.Length < position) {
        LogMessage("step3b: date fill skipped - only " . wrappers.Length . " BravoDateEdit present (wanted #" . position . ")")
        return
    }
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
    try {
        wrappers[position]["elem"].Value := mdY
        Sleep(150)
        Send("{Tab}")
        Sleep(150)
        LogMessage("step3b: date #" . position . " filled with " . mdY)
    } catch as e {
        LogMessage("step3b: date #" . position . " fill failed: " . e.Message)
    }
}

DumpEditsAll() {
    try {
        root := GetBravoRoot()
        els := root.FindElements({Type: "Edit"})
        for e in els {
            n := ""
            a := ""
            v := ""
            rs := ""
            try n := e.Name
            try a := e.AutomationId
            try v := e.Value
            try {
                r := e.BoundingRectangle
                rs := r.l . "," . r.t
            }
            LogMessage("[edit] " . Chr(39) . n . Chr(39) . " aid=" . Chr(39) . a . Chr(39) . " val=" . Chr(39) . v . Chr(39) . " @" . rs)
        }
    }
}
