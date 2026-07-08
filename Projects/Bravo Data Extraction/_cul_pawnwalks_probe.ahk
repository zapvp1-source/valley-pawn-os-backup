; READ-ONLY probe at CUL (a WORKING store): load "Claude Pawn Walks" and dump
; the dialog criteria area + all Edit controls. Tells us exactly what field /
; operator / editors the GOOD definition uses, so the LEX rebuild can copy it.
; Result: logs\_culpw_probe_result.txt
#Requires AutoHotkey v2.0
#SingleInstance Off
#Include lib\Json.ahk
#Include lib\Bravo.ahk
#Include lib\StoreCycle.ahk

global CONFIG := Map()
CONFIG["paths.logs"]     := A_ScriptDir . "\logs"
CONFIG["bravo.username"] := "FREE1@WAY"
CONFIG["bravo.password"] := "Health2035!"

global RES := CONFIG["paths.logs"] . "\_culpw_probe_result.txt"
WriteRes(s) {
    global RES
    try FileDelete(RES)
    try FileAppend(s, RES, "UTF-8")
}

InitLog(CONFIG["paths.logs"], "culpw-probe-" . FormatTime(, "yyyyMMdd-HHmmss"))
LogMessage("=== CUL probe start ===")
WriteRes("RUNNING")

ActivateBravo()
Sleep(800)
if !EnsureStore("CUL", CONFIG["bravo.password"]) {
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
} catch as e {
    LogMessage("WARN select: " . e.Message)
}
Sleep(1200)

LogMessage("--- dialog Texts (criteria area) ---")
DumpTextsInBox(400, 430, 2400, 1700)
LogMessage("--- all Edits ---")
DumpEditsAll()

WriteRes("OK")
try ClickByName("Cancel", 3000)
Sleep(800)
try ClickByName("Cancel", 3000)
Sleep(800)
try DismissPopups()
try BackToDashboard()
LogMessage("=== CUL probe done ===")
ExitApp(0)

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
