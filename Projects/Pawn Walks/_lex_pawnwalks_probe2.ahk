; One-off READ-ONLY probe #2 at LEX: load "Claude Pawn Walks" (Enter-commit),
; then open the BoxSelectCriteria and BoxColumns dropdowns and dump their
; option lists + the current criteria rows, so the rebuild script can be
; written precisely. Exits via Cancel - saves nothing.
; Result: logs\_lexpw_probe2_result.txt
#Requires AutoHotkey v2.0
#SingleInstance Off
#Include lib\Json.ahk
#Include lib\Bravo.ahk
#Include lib\StoreCycle.ahk

global CONFIG := Map()
CONFIG["paths.logs"]     := A_ScriptDir . "\logs"
CONFIG["bravo.username"] := "FREE1@WAY"
CONFIG["bravo.password"] := "Health2035!"

global RES := CONFIG["paths.logs"] . "\_lexpw_probe2_result.txt"
WriteRes(s) {
    global RES
    try FileDelete(RES)
    try FileAppend(s, RES, "UTF-8")
}

InitLog(CONFIG["paths.logs"], "lexpw-probe2-" . FormatTime(, "yyyyMMdd-HHmmss"))
LogMessage("=== LEX probe2 start ===")
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

; --- load Claude Pawn Walks with Enter-commit --------------------------------
combo := FindComboByAid("")  ; bottom-most generic
try {
    c := LexFindBottomCombo()
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
} catch as e {
    LogMessage("WARN select: " . e.Message)
}
LogMessage("loaded (list open=" . (ExistsByName("<new report>") ? "STILL OPEN" : "closed") . ")")
Sleep(800)

LogMessage("--- A: current dialog Texts x in 400..2300, y in 430..1700 (criteria area) ---")
DumpTextsInBox(400, 430, 2300, 1700)

LogMessage("--- B: open BoxSelectCriteria dropdown ---")
critCombo := FindComboByAid("BoxSelectCriteria")
if critCombo {
    try critCombo.Click("left")
    Sleep(1000)
    DumpTextsInBox(0, 0, 3400, 2160)
    Send("{Esc}")
    Sleep(700)
} else {
    LogMessage("WARN BoxSelectCriteria not found")
}

LogMessage("--- C: open BoxColumns dropdown ---")
colCombo := FindComboByAid("BoxColumns")
if colCombo {
    try colCombo.Click("left")
    Sleep(1000)
    DumpTextsInBox(0, 0, 3400, 2160)
    DumpType("ListItem")
    DumpType("CheckBox")
    Send("{Esc}")
    Sleep(700)
} else {
    LogMessage("WARN BoxColumns not found")
}

WriteRes("OK")
try ClickByName("Cancel", 3000)
Sleep(800)
try ClickByName("Cancel", 3000)
Sleep(800)
try DismissPopups()
try BackToDashboard()
LogMessage("=== probe2 done ===")
ExitApp(0)

FindComboByAid(aid) {
    try {
        root := GetBravoRoot()
        els := root.FindElements({Type: "Edit"})
        for e in els {
            a := ""
            try a := e.AutomationId
            if (a = aid && aid != "")
                return e
        }
    }
    return 0
}

LexFindBottomCombo() {
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
            if (cnt > 150)
                break
            LogMessage("[t] " . Chr(39) . n . Chr(39) . " @" . r.l . "," . r.t)
        }
    }
}

DumpType(typeName) {
    try {
        root := GetBravoRoot()
        els := root.FindElements({Type: typeName})
        cnt := 0
        for e in els {
            cnt++
            if (cnt > 100)
                break
            n := ""
            a := ""
            r := 0
            rs := ""
            try n := e.Name
            try a := e.AutomationId
            try r := e.BoundingRectangle
            if r
                rs := r.l . "," . r.t
            LogMessage("[" . typeName . "] " . Chr(39) . n . Chr(39) . " aid=" . Chr(39) . a . Chr(39) . " @" . rs)
        }
    }
}
