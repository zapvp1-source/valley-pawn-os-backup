; One-off: at LEX, find a selection method that actually COMMITS the
; "Claude Pawn Walks" saved-report pick (plain ClickByName leaves the
; dropdown open on this store). Tries: click -> double-click -> Enter.
; Verifies commit by the dropdown closing ('<new report>' disappearing),
; then dumps the loaded criteria/edit area so we can confirm the report
; definition is the good global one. READ-ONLY: exits via Cancel.
; Result: logs\_lexpw_commit_result.txt = OK <method> / FAIL <reason>
#Requires AutoHotkey v2.0
#SingleInstance Off
#Include lib\Json.ahk
#Include lib\Bravo.ahk
#Include lib\StoreCycle.ahk

global CONFIG := Map()
CONFIG["paths.logs"]     := A_ScriptDir . "\logs"
CONFIG["bravo.username"] := "FREE1@WAY"
CONFIG["bravo.password"] := "Health2035!"

global RES := CONFIG["paths.logs"] . "\_lexpw_commit_result.txt"
WriteRes(s) {
    global RES
    try FileDelete(RES)
    try FileAppend(s, RES, "UTF-8")
}

InitLog(CONFIG["paths.logs"], "lexpw-commit-" . FormatTime(, "yyyyMMdd-HHmmss"))
LogMessage("=== LEX PawnWalks COMMIT test start ===")
WriteRes("RUNNING")

ActivateBravo()
Sleep(800)
if !EnsureStore("LEX", CONFIG["bravo.password"]) {
    WriteRes("FAIL EnsureStore LEX")
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

method := ""
combo := LexFindBottomCombo()
if !combo {
    WriteRes("FAIL no saved-report combo")
    CleanExit(1)
}
try combo.Click("left")
Sleep(900)

if !ExistsByName("<new report>") {
    LogMessage("WARN dropdown did not open on first combo click - clicking again")
    try combo.Click("left")
    Sleep(900)
}

; Attempt 1: plain click (known to fail on LEX, but try for the record)
try ClickByName("Claude Pawn Walks", 3000)
Sleep(1200)
if !ExistsByName("<new report>") {
    method := "click"
} else {
    LogMessage("click did not commit (list still open) - trying double-click")
    try DoubleClickByName("Claude Pawn Walks", 3000)
    Sleep(1200)
    if !ExistsByName("<new report>") {
        method := "double-click"
    } else {
        LogMessage("double-click did not commit - trying Enter")
        Send("{Enter}")
        Sleep(1200)
        if !ExistsByName("<new report>") {
            method := "enter"
        }
    }
}

if (method = "") {
    LogMessage("no commit method worked - dumping list state")
    LogVisibleNames()
    WriteRes("FAIL no commit method worked")
    CleanExit(1)
}
LogMessage("COMMIT OK via: " . method)

; Give the definition time to load, then dump what's in the criteria area
Sleep(1500)
hasTxn := ExistsByName("Transaction Date")
LogMessage("criteria check: Transaction Date present=" . (hasTxn ? "YES" : "no"))
DumpTexts()
DumpEdits()

WriteRes("OK " . method . (hasTxn ? " txn-date=yes" : " txn-date=no"))
CleanExit(0)

CleanExit(code) {
    try ClickByName("Cancel", 3000)
    Sleep(800)
    try ClickByName("Cancel", 3000)
    Sleep(800)
    try DismissPopups()
    try BackToDashboard()
    LogMessage("=== COMMIT test done ===")
    ExitApp(code)
}

DumpTexts() {
    try {
        root := GetBravoRoot()
        els := root.FindElements({Type: "Text"})
        cnt := 0
        for e in els {
            cnt++
            if (cnt > 120)
                break
            n := ""
            rs := ""
            try n := e.Name
            if (n = "")
                continue
            try {
                r := e.BoundingRectangle
                rs := r.l . "," . r.t
            }
            LogMessage("[text] " . Chr(39) . n . Chr(39) . " @" . rs)
        }
    }
}

DumpEdits() {
    try {
        root := GetBravoRoot()
        els := root.FindElements({Type: "Edit"})
        for e in els {
            n := ""
            aid := ""
            val := ""
            rs := ""
            try n := e.Name
            try aid := e.AutomationId
            try val := e.Value
            try {
                r := e.BoundingRectangle
                rs := r.l . "," . r.t
            }
            LogMessage("[edit] " . Chr(39) . n . Chr(39) . " aid=" . Chr(39) . aid . Chr(39) . " val=" . Chr(39) . val . Chr(39) . " @" . rs)
        }
    }
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
