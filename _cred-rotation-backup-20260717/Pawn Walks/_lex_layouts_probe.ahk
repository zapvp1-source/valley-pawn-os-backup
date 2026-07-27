; READ-ONLY: at LEX, run Claude Pawn Walks, then dump the Layouts panel and
; the contents of the Saved Layouts dropdown. No changes saved.
; Result: logs\_lex_layouts_probe_result.txt
#Requires AutoHotkey v2.0
#SingleInstance Off
#Include lib\Json.ahk
#Include lib\Bravo.ahk
#Include lib\StoreCycle.ahk

global CONFIG := Map()
CONFIG["paths.logs"]     := A_ScriptDir . "\logs"
CONFIG["bravo.username"] := "FREE1@WAY"
CONFIG["bravo.password"] := "Health2035!"

global RES := CONFIG["paths.logs"] . "\_lex_layouts_probe_result.txt"
WriteRes(s) {
    global RES
    try FileDelete(RES)
    try FileAppend(s, RES, "UTF-8")
}

InitLog(CONFIG["paths.logs"], "lex-layouts-probe-" . FormatTime(, "yyyyMMdd-HHmmss"))
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
        throw Error("list did not render")
    Sleep(4000)
} catch as e {
    WriteRes("FAIL setup: " . e.Message)
    CleanExit(1)
}

LogMessage("--- Layouts panel area dump (x500-1800, y300-700) ---")
DumpAll(500, 300, 1800, 700)

; open the Saved Layouts dropdown with a physical double-click
lblY := TextYInBox("Saved Layouts", 500, 400, 900, 700)
LogMessage("Saved Layouts label y=" . lblY)
combo := FindComboNearRow(lblY)
if combo {
    r := 0
    try r := combo.BoundingRectangle
    if r {
        LogMessage("combo @" . r.l . "," . r.t . " " . (r.r - r.l) . "x" . (r.b - r.t))
        CoordMode("Mouse", "Screen")
        Click((r.l + r.r) // 2, (r.t + r.b) // 2, 2)
        Sleep(1500)
    }
    LogMessage("--- FULL dump after opening Saved Layouts dropdown ---")
    DumpAll(0, 0, 3400, 2160)
    Send("{Esc}")
    Sleep(600)
} else {
    LogMessage("no Saved Layouts combo found")
}

WriteRes("OK")
CleanExit(0)

CleanExit(code) {
    try ClickByName("Cancel", 3000)
    Sleep(800)
    try ClickByName("Cancel", 3000)
    Sleep(800)
    try DismissPopups()
    try BackToDashboard()
    ExitApp(code)
}

DumpAll(x1, y1, x2, y2) {
    for typeName in ["Text", "ListItem", "Button", "Edit", "CheckBox"] {
        cnt := 0
        try {
            root := GetBravoRoot()
            els := root.FindElements({Type: typeName})
            for e in els {
                n := ""
                a := ""
                v := ""
                try n := e.Name
                try a := e.AutomationId
                try v := e.Value
                r := 0
                try r := e.BoundingRectangle
                if !r
                    continue
                if (r.l < x1 || r.l > x2 || r.t < y1 || r.t > y2)
                    continue
                if (n = "" && a = "" && v = "")
                    continue
                cnt++
                if (cnt > 150)
                    break
                LogMessage("[" . typeName . "] n=" . Chr(39) . n . Chr(39) . " aid=" . Chr(39) . a . Chr(39) . " v=" . Chr(39) . v . Chr(39) . " @" . r.l . "," . r.t)
            }
        }
    }
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
