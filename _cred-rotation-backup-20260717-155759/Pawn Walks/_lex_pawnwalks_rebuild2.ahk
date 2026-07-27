; Rebuild "Claude Pawn Walks" at LEX to EXACTLY match the working CUL
; definition (probed read-only 2026-06-12):
;   columns layout : 'Full description and cost' (Object_Layout 490f2277-...)
;   criteria 1     : Disposition Date  range  [date1][date2]  (BravoDateEdit x2)
;   criteria 2     : Ticket Kind = BUY
; STRICT SANITY GATE before Save; cancels without saving on any mismatch.
; Result: logs\_lexpw_rebuild2_result.txt = SAVED / NOSAVE <reason> / FAIL <reason>
#Requires AutoHotkey v2.0
#SingleInstance Off
#Include lib\Json.ahk
#Include lib\Bravo.ahk
#Include lib\StoreCycle.ahk

global CONFIG := Map()
CONFIG["paths.logs"]     := A_ScriptDir . "\logs"
CONFIG["bravo.username"] := "FREE1@WAY"
CONFIG["bravo.password"] := "Health2035!"

global RES := CONFIG["paths.logs"] . "\_lexpw_rebuild2_result.txt"
WriteRes(s) {
    global RES
    try FileDelete(RES)
    try FileAppend(s, RES, "UTF-8")
}

InitLog(CONFIG["paths.logs"], "lexpw-rebuild2-" . FormatTime(, "yyyyMMdd-HHmmss"))
LogMessage("=== LEX REBUILD v2 start ===")
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

; --- 1. load Claude Pawn Walks --------------------------------------------------
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

; --- 2. columns layout = 'Full description and cost' -----------------------------
layoutOk := false
try {
    colCombo := FindComboByAid("BoxColumns")
    if !colCombo
        throw Error("BoxColumns not found")
    colCombo.Click("left")
    Sleep(1000)
    if !ExistsByName("Full description and cost")
        throw Error("layout list did not show Full description and cost")
    ClickByName("Full description and cost", 3000)
    Sleep(900)
    if ExistsByName("Trade In View") {
        Send("{Enter}")
        Sleep(900)
    }
    if ExistsByName("Trade In View")
        throw Error("layout selection would not commit")
    v := ""
    try v := FindComboByAid("BoxColumns").Value
    LogMessage("step2: BoxColumns value now: " . v)
    if InStr(v, "490f2277")
        layoutOk := true
    else
        LogMessage("step2 WARN: expected GUID 490f2277 not in BoxColumns value")
} catch as e {
    LogMessage("step2 FAILED: " . e.Message)
}

; --- 3. criteria: Disposition Date (range) ---------------------------------------
dispOk := false
try {
    AddCriteria("Disposition Date")
    Sleep(900)
    if !TextExistsInBox("Disposition Date", 500, 600, 700, 1700)
        throw Error("Disposition Date criteria row did not appear")
    LogMessage("step3: Disposition Date row added")
    ; operator: needs to read 'range' like CUL
    if !TextExistsInBox("range", 700, 600, 1300, 1700) {
        LogMessage("step3: operator not range yet - opening operator dropdown")
        opEl := FindTextRightOf("Disposition Date", 600, 1700)
        if opEl {
            opEl.Click("left")
            Sleep(900)
            if ExistsByName("range") {
                ClickByName("range", 2500)
                Sleep(900)
            }
            if !TextExistsInBox("range", 700, 600, 1300, 1700) {
                Send("{Enter}")
                Sleep(700)
            }
        }
    }
    if TextExistsInBox("range", 700, 600, 1300, 1700) {
        dispOk := true
        LogMessage("step3: operator = range OK")
    } else {
        LogMessage("step3 WARN: operator is not range - dumping row area")
        DumpTextsInBox(400, 600, 2400, 1700)
    }
} catch as e {
    LogMessage("step3 FAILED: " . e.Message)
}

; --- 4. fill the two date editors -------------------------------------------------
datesOk := 0
datesOk += LexFillDate(1, "6/11/2026") ? 1 : 0
datesOk += LexFillDate(2, "6/11/2026") ? 1 : 0

; --- 5. REQUIRED GATE + SAVE #1 (layout + date range - the critical core) ----------
LogMessage("--- pre-save#1 state: layoutOk=" . layoutOk . " dispOk=" . dispOk . " datesOk=" . datesOk . " ---")
if !(layoutOk && dispOk && datesOk = 2) {
    WriteRes("NOSAVE layoutOk=" . layoutOk . " dispOk=" . dispOk . " datesOk=" . datesOk)
    LogMessage("required gate failed - cancelling, nothing saved")
    CleanExit(1)
}
saveBtn := FindButtonInBox("Save", 2100, 450, 2450, 700)
if !saveBtn {
    WriteRes("NOSAVE dialog Save button not found")
    CleanExit(1)
}
try {
    saveBtn.Click("left")
    Sleep(1500)
    LogMessage("step5: SAVE #1 done (layout + Disposition Date range)")
    try DismissPopups()
    Sleep(800)
} catch as e {
    WriteRes("FAIL save click: " . e.Message)
    CleanExit(1)
}
WriteRes("SAVED-CORE")

; --- 6. attempt Ticket Kind = BUY as a separate second save ------------------------
; If this fails at any point we Cancel and the core save above stands.
if !FindButtonInBox("Save", 2100, 450, 2450, 700) {
    LogMessage("step6: dialog closed after save - reopening")
    try {
        DismissPopups()
        ClickByName("Custom Reports", 5000)
        Sleep(1500)
        c2 := FindBottomSavedReportCombo()
        if c2 {
            c2.Click("left")
            Sleep(900)
        }
        ClickByName("Claude Pawn Walks", 3000)
        Sleep(900)
        if ExistsByName("<new report>") {
            Send("{Enter}")
            Sleep(1200)
        }
        Sleep(800)
    } catch as e {
        LogMessage("step6: reopen failed: " . e.Message . " - keeping core save")
        WriteRes("SAVED core-only (reopen failed; BUY filter via downstream BT- filter)")
        CleanExit(0)
    }
}
kindOk := false
try {
    AddCriteria("Ticket Kind")
    Sleep(900)
    if !TextExistsInBox("Ticket Kind", 500, 600, 700, 1700)
        throw Error("Ticket Kind criteria row did not appear")
    LogMessage("step5: Ticket Kind row added")
    ; value combo: the BravoComboBox on the Ticket Kind row; pick BUY
    kindRowY := TextYInBox("Ticket Kind", 500, 600, 700, 1700)
    valCombo := FindComboNearRow(kindRowY)
    if !valCombo
        throw Error("Ticket Kind value combo not found")
    r := 0
    try r := valCombo.BoundingRectangle
    if r
        LogMessage("step5: value combo rect " . r.l . "," . r.t . " " . (r.r - r.l) . "x" . (r.b - r.t))
    ; physical double-click on the combo center (act like a human)
    if r {
        CoordMode("Mouse", "Screen")
        Click((r.l + r.r) // 2, (r.t + r.b) // 2, 2)
        Sleep(1300)
    }
    ; find the option under any plausible name
    optEl := 0
    optName := ""
    for cand in ["BUY", "Buy", "TKBUY", "Buy Ticket", "buy"] {
        optEl := FindByName(cand, 800)
        if optEl {
            optName := cand
            break
        }
    }
    if optEl {
        LogMessage("step5: option " . optName . " visible")
        li2 := FindListItemContaining(optEl)
        if li2 {
            try {
                li2.SelectionItemPattern.Select()
                Sleep(900)
                LogMessage("step5: " . optName . " selected via SelectionItemPattern")
            } catch as e {
                try optEl.Click("left")
                Sleep(900)
            }
        } else {
            try optEl.Click("left")
            Sleep(900)
        }
        v := ""
        try v := FindComboNearRow(kindRowY).Value
        if !InStr(v, "BUY") {
            Send("{Enter}")
            Sleep(900)
        }
    } else {
        ; dropdown options not visible - wide dump for diagnosis
        LogMessage("step5: no BUY option visible after F4 - wide dump")
        DumpTextsInBox(0, 900, 3400, 2100)
        Send("{Esc}")
        Sleep(500)
        ; direct ValuePattern writes (display text, then lookup code)
        for tryVal in ["BUY", "TKBUY"] {
            vc := FindComboNearRow(kindRowY)
            ti := vc ? FindInnerEditor(vc) : 0
            t2 := ti ? ti : vc
            if !t2
                break
            try {
                t2.Value := tryVal
                Sleep(500)
                Send("{Tab}")
                Sleep(700)
            }
            v := ""
            try v := FindComboNearRow(kindRowY).Value
            LogMessage("step5: after Value:=" . tryVal . " combo value=" . Chr(39) . v . Chr(39))
            if InStr(v, "BUY")
                break
        }
        ; last resort: focused typing
        v := ""
        try v := FindComboNearRow(kindRowY).Value
        if !InStr(v, "BUY") {
            vc := FindComboNearRow(kindRowY)
            ti := vc ? FindInnerEditor(vc) : 0
            t2 := ti ? ti : vc
            if t2 {
                try t2.Focus()
                Sleep(400)
                Send("BUY")
                Sleep(500)
                Send("{Tab}")
                Sleep(800)
            }
        }
    }
    v := ""
    try v := FindComboNearRow(kindRowY).Value
    LogMessage("step5: Ticket Kind combo value: " . v)
    if InStr(v, "BUY") || InStr(v, "TKBUY")
        kindOk := true
    else if TextExistsInBox("BUY", 900, 600, 1400, 1700)
        kindOk := true
} catch as e {
    LogMessage("step6 (Ticket Kind) FAILED: " . e.Message)
}

if kindOk {
    saveBtn2 := FindButtonInBox("Save", 2100, 450, 2450, 700)
    if saveBtn2 {
        try {
            saveBtn2.Click("left")
            Sleep(1500)
            try DismissPopups()
            Sleep(800)
            WriteRes("SAVED full (with Ticket Kind=BUY)")
            LogMessage("=== REBUILD v2: SAVED FULL ===")
            CleanExit(0)
        }
    }
    WriteRes("SAVED core-only (2nd Save button missing)")
    CleanExit(0)
} else {
    LogMessage("step6: BUY not settable - cancelling 2nd edit; core save stands")
    DumpTextsInBox(400, 430, 2400, 1700)
    WriteRes("SAVED core-only (BUY not settable; downstream BT- filter needed)")
    CleanExit(0)
}

; ------------------------------------------------------------------ helpers ---
AddCriteria(optionName) {
    critCombo := FindComboByAid("BoxSelectCriteria")
    if !critCombo
        throw Error("BoxSelectCriteria not found")
    critCombo.Click("left")
    Sleep(1000)
    if ExistsByName(optionName) {
        ; visible without scrolling: plain click commits (proven)
        ClickByName(optionName, 3000)
        Sleep(900)
        if ExistsByName("Firearm Action") {
            LogMessage("    [criteria] options list still open - sending Enter")
            Send("{Enter}")
            Sleep(900)
        }
        return
    }
    ; option below the visible window: scroll via UIA ScrollPattern, then
    ; select via SelectionItemPattern (physical click after a scroll snaps
    ; the popup back without committing - confirmed)
    LogMessage("    [criteria] " . optionName . " not visible - ScrollPattern scroll")
    lst := FindPopupList()
    if !lst
        throw Error("no scrollable popup container found for " . optionName)
    found := false
    v := 0.0
    while (v <= 100) {
        try lst.ScrollPattern.SetScrollPercent(v)
        Sleep(400)
        if ExistsByName(optionName) {
            found := true
            break
        }
        v := v + 10
    }
    if !found
        throw Error(optionName . " not visible in criteria options after scroll")
    el := FindByName(optionName, 2000)
    li := el ? FindListItemContaining(el) : 0
    selected := false
    if li {
        try {
            li.SelectionItemPattern.Select()
            Sleep(1100)
            selected := true
            LogMessage("    [criteria] " . optionName . " selected via SelectionItemPattern")
        } catch as e {
            LogMessage("    [criteria] SelectionItemPattern failed: " . e.Message)
        }
    } else {
        LogMessage("    [criteria] no containing ListItem found for " . optionName)
    }
    if !selected {
        ClickByName(optionName, 3000)
        Sleep(900)
    }
    ; Select() only highlights - commit with Enter if the popup is still open
    ; (popup option texts sit at x~481; criteria-row labels at x~517)
    if (TextYInBox(optionName, 450, 600, 499, 1700) >= 0) {
        LogMessage("    [criteria] popup still open after select - Enter to commit")
        Send("{Enter}")
        Sleep(1000)
    }
}

; inner PART_Editor Edit nested inside the given wrapper element's rect
FindInnerEditor(wrapper) {
    wr := 0
    try wr := wrapper.BoundingRectangle
    if !wr
        return 0
    try {
        root := GetBravoRoot()
        els := root.FindElements({Type: "Edit"})
        for e in els {
            a := ""
            try a := e.AutomationId
            if (a != "PART_Editor")
                continue
            r := 0
            try r := e.BoundingRectangle
            if !r
                continue
            if (r.l >= wr.l && r.r <= wr.r && r.t >= wr.t && r.b <= wr.b)
                return e
        }
    }
    return 0
}

; ListItem whose bounding rect contains the given element's center
FindListItemContaining(el) {
    r := 0
    try r := el.BoundingRectangle
    if !r
        return 0
    cx := (r.l + r.r) // 2
    cy := (r.t + r.b) // 2
    try {
        root := GetBravoRoot()
        items := root.FindElements({Type: "ListItem"})
        for it in items {
            ir := 0
            try ir := it.BoundingRectangle
            if !ir
                continue
            if (cx >= ir.l && cx <= ir.r && cy >= ir.t && cy <= ir.b)
                return it
        }
    }
    return 0
}

; the scrollable container of the open criteria-options popup: any element in
; the popup region (x ~450-800, tall) exposing ScrollPattern
FindPopupList() {
    try {
        root := GetBravoRoot()
        for typeName in ["List", "Pane", "Tree", "Table", "Group", "Custom"] {
            els := root.FindElements({Type: typeName})
            for e in els {
                r := 0
                try r := e.BoundingRectangle
                if !r
                    continue
                if (r.l < 400 || r.l > 900)
                    continue
                if (r.t < 550 || r.t > 1000)
                    continue
                if ((r.b - r.t) < 250)
                    continue
                ok := false
                try ok := e.IsScrollPatternAvailable
                if ok {
                    LogMessage("    [criteria] popup container: " . typeName . " @" . r.l . "," . r.t)
                    return e
                }
            }
        }
    }
    return 0
}

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

; first Text named `name` with x,y inside box -> returns its y (or -1)
TextYInBox(name, x1, y1, x2, y2) {
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
                return r.t
        }
    }
    return -1
}

TextExistsInBox(name, x1, y1, x2, y2) {
    return TextYInBox(name, x1, y1, x2, y2) >= 0
}

; clickable Text element directly right of the named criteria label (same row)
FindTextRightOf(labelName, y1, y2) {
    try {
        root := GetBravoRoot()
        lblY := TextYInBox(labelName, 400, y1, 1200, y2)
        if (lblY < 0)
            return 0
        txts := root.FindElements({Type: "Text"})
        best := 0
        bestX := 99999
        for t in txts {
            n := ""
            try n := t.Name
            if (n = "" || n = labelName)
                continue
            r := 0
            try r := t.BoundingRectangle
            if !r
                continue
            if (Abs(r.t - lblY) > 40)
                continue
            if (r.l < 700 || r.l > 1400)
                continue
            if (r.l < bestX) {
                bestX := r.l
                best := t
            }
        }
        return best
    }
    return 0
}

; BravoComboBox on roughly the given row y (+-50)
FindComboNearRow(rowY) {
    if (rowY < 0)
        return 0
    try {
        root := GetBravoRoot()
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
            if (Abs(r.t - rowY) > 50)
                continue
            if (r.l < 700)
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
        LogMessage("step4: date #" . position . " skipped - only " . wrappers.Length . " BravoDateEdit present")
        return false
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
        LogMessage("step4: date #" . position . " = " . mdY)
        return true
    } catch as e {
        LogMessage("step4: date #" . position . " fill failed: " . e.Message)
        return false
    }
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
