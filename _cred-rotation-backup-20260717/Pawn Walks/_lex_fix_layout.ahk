; Fix the LEX Loans/Buys Custom Reports LIST VIEW grid layout: run the (now
; correct) "Claude Pawn Walks" report, then set the list view's Saved Layouts
; to 'Full description and cost' so exports carry the right 4 columns.
; Result: logs\_lex_fix_layout_result.txt
#Requires AutoHotkey v2.0
#SingleInstance Off
#Include lib\Json.ahk
#Include lib\Bravo.ahk
#Include lib\StoreCycle.ahk

global CONFIG := Map()
CONFIG["paths.logs"]     := A_ScriptDir . "\logs"
CONFIG["bravo.username"] := "FREE1@WAY"
CONFIG["bravo.password"] := "Health2035!"

global RES := CONFIG["paths.logs"] . "\_lex_fix_layout_result.txt"
WriteRes(s) {
    global RES
    try FileDelete(RES)
    try FileAppend(s, RES, "UTF-8")
}

InitLog(CONFIG["paths.logs"], "lex-fix-layout-" . FormatTime(, "yyyyMMdd-HHmmss"))
LogMessage("=== LEX fix list-view layout start ===")
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
    Sleep(800)
    ClickByName("Ok", 5000)
    if !FindByName("Layouts", 30000)
        throw Error("list did not render (no Layouts)")
    Sleep(4000)
} catch as e {
    WriteRes("FAIL setup: " . e.Message)
    CleanExit(1)
}

; --- set Saved Layouts -> 'Full description and cost' ----------------------------
ok := false
try {
    ; the Saved Layouts combo sits right of the 'Saved Layouts' label (~y 516)
    lblY := TextYInBox("Saved Layouts", 500, 400, 900, 700)
    if (lblY < 0) {
        ; panel may be collapsed - click the Layouts caret
        LogMessage("Saved Layouts label not visible - clicking Layouts caret")
        ClickByName("Layouts", 3000)
        Sleep(1200)
        lblY := TextYInBox("Saved Layouts", 500, 400, 900, 700)
    }
    if (lblY < 0)
        throw Error("Saved Layouts label not found")
    combo := FindComboNearRow(lblY)
    if !combo
        throw Error("Saved Layouts combo not found")
    r := 0
    try r := combo.BoundingRectangle
    LogMessage("Saved Layouts combo @" . (r ? r.l . "," . r.t : "?"))
    ; physical double-click opens these DevExpress combos reliably
    if r {
        CoordMode("Mouse", "Screen")
        Click((r.l + r.r) // 2, (r.t + r.b) // 2, 2)
        Sleep(1300)
    }
    optEl := FindByName("Full description and cost", 2500)
    if !optEl
        throw Error("layout option not visible after opening combo")
    li := FindListItemContaining(optEl)
    if li {
        try {
            li.SelectionItemPattern.Select()
            Sleep(1000)
            LogMessage("layout selected via SelectionItemPattern")
        } catch as e {
            try optEl.Click("left")
            Sleep(1000)
        }
    } else {
        try optEl.Click("left")
        Sleep(1000)
    }
    ; commit if popup still open
    if (TextYInBox("Pawn Walk", 400, 400, 2400, 2000) >= 0) {
        Send("{Enter}")
        Sleep(1000)
    }
    Sleep(2500)
    ; verify the grid header switched to the 4-column layout
    if (TextYInBox("Full Description", 400, 350, 2700, 520) >= 0
        || TextYInBox("Category", 400, 350, 2700, 520) >= 0) {
        ok := true
        LogMessage("grid header now shows Category/Full Description - layout applied")
    } else {
        LogMessage("WARN: grid header did not change - dumping header texts")
        DumpTextsInBox(400, 350, 2700, 560)
    }
} catch as e {
    LogMessage("FAILED: " . e.Message)
}

WriteRes(ok ? "OK layout applied" : "FAIL layout not applied")
CleanExit(ok ? 0 : 1)

CleanExit(code) {
    try ClickByName("Cancel", 3000)
    Sleep(800)
    try ClickByName("Cancel", 3000)
    Sleep(800)
    try DismissPopups()
    try BackToDashboard()
    LogMessage("=== exit " . code . " ===")
    ExitApp(code)
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
            if (Abs(r.t - rowY) > 60)
                continue
            if (r.l < 600)
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
            if (cnt > 100)
                break
            LogMessage("[t] " . Chr(39) . n . Chr(39) . " @" . r.l . "," . r.t)
        }
    }
}
