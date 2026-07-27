; One-off DIAGNOSTIC (read-only): at LEX, open Loans/Buys -> Custom Reports,
; select saved report "Claude Pawn Walks", then deep-dump every control
; (type/name/AutomationId/value/rect) so we can script the rebuild precisely.
; Makes NO changes - exits via Cancel + BackToDashboard.
; Result file: logs\_lexpw_diag_result.txt = OK / FAIL <reason>
#Requires AutoHotkey v2.0
#SingleInstance Off
#Include lib\Json.ahk
#Include lib\Bravo.ahk
#Include lib\StoreCycle.ahk

global CONFIG := Map()
CONFIG["paths.logs"]     := A_ScriptDir . "\logs"
CONFIG["bravo.username"] := "FREE1@WAY"
CONFIG["bravo.password"] := "Health2035!"

global RES := CONFIG["paths.logs"] . "\_lexpw_diag_result.txt"
WriteRes(s) {
    global RES
    try FileDelete(RES)
    try FileAppend(s, RES, "UTF-8")
}

InitLog(CONFIG["paths.logs"], "lexpw-diag-" . FormatTime(, "yyyyMMdd-HHmmss"))
LogMessage("=== LEX PawnWalks DIAG start ===")
WriteRes("RUNNING")

ActivateBravo()
Sleep(800)
if !EnsureStore("LEX", CONFIG["bravo.password"]) {
    WriteRes("FAIL EnsureStore LEX")
    ExitApp(1)
}
LogMessage("on LEX")
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

LogMessage("--- DUMP 1: dialog as opened (before selecting report) ---")
DeepDumpControls()

; Select the saved report (same approach as the handlers)
selected := false
try {
    combo := LexFindBottomCombo()
    if combo {
        try combo.Click("left")
        Sleep(800)
    }
    ClickByName("Claude Pawn Walks", 3000)
    Sleep(1500)
    selected := true
    LogMessage("selected Claude Pawn Walks")
} catch as e {
    LogMessage("WARN select failed: " . e.Message)
}

LogMessage("--- DUMP 2: after selecting Claude Pawn Walks (selected=" . (selected ? "yes" : "no") . ") ---")
DeepDumpControls()

; Read-only exit
try ClickByName("Cancel", 3000)
Sleep(800)
try ClickByName("Cancel", 3000)
Sleep(800)
try DismissPopups()
try BackToDashboard()
WriteRes(selected ? "OK" : "OK-noselect")
LogMessage("=== DIAG done ===")
ExitApp(0)

DeepDumpControls() {
    root := ""
    try root := GetBravoRoot()
    if (root = "") {
        LogMessage("[dump] no root")
        return
    }
    for typeName in ["Edit", "Button", "CheckBox", "Text", "ListItem", "DataItem", "TreeItem", "TabItem"] {
        cnt := 0
        try {
            els := root.FindElements({Type: typeName})
            for e in els {
                cnt++
                if (cnt > 150) {
                    LogMessage("[dump] " . typeName . " truncated at 150")
                    break
                }
                n := ""
                aid := ""
                val := ""
                rs := ""
                try n := e.Name
                try aid := e.AutomationId
                try val := e.Value
                try {
                    r := e.BoundingRectangle
                    rs := r.l . "," . r.t . " " . (r.r - r.l) . "x" . (r.b - r.t)
                }
                LogMessage("[dump] " . typeName . " | name=" . Chr(39) . n . Chr(39) . " aid=" . Chr(39) . aid . Chr(39) . " val=" . Chr(39) . val . Chr(39) . " @" . rs)
            }
        } catch as ex {
            LogMessage("[dump] " . typeName . " ERR " . ex.Message)
        }
        LogMessage("[dump] " . typeName . " total=" . cnt)
    }
}

; bottom-most BravoComboBox = the Choose Saved Report combo (same heuristic
; as FindSavedReportCombo in the report handlers)
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
            autoId := ""
            try autoId := e.AutomationId
            if (autoId = "BoxColumns" || autoId = "BoxIsShared" || autoId = "BoxSelectCriteria")
                continue
            rect := 0
            try rect := e.BoundingRectangle
            if !rect
                continue
            y := 0
            try y := rect.t
            if (y > bestY) {
                bestY := y
                bestElem := e
            }
        }
    }
    return bestElem
}
