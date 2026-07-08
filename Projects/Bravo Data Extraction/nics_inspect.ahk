; nics_inspect.ahk — full UIA inspection of the Void/View Transactions Custom
; Reports criteria dialog for "Claude NICS Transfers", run against WAY (has data).
; Captures: saved-report combo AutomationId, fee-type combo (contains "NICS Fee"),
; and date-edit structure. Read-only intent (Cancels out, runs nothing).
#Requires AutoHotkey v2.0
SetWorkingDir(A_ScriptDir)
#Include lib\Json.ahk
#Include lib\Bravo.ahk

global ILOG := A_ScriptDir . "\logs\nics_inspect.log"
global IRES := A_ScriptDir . "\logs\nics_inspect_result.txt"
D(m) {
    global ILOG
    try FileAppend(FormatTime(, "HH:mm:ss") . "  " . m . "`r`n", ILOG, "UTF-8")
}
try FileDelete(ILOG)
try FileDelete(IRES)
D("=== nics_inspect start ===")

password := ""
try {
    cfg := Json.Load(&(FileRead(A_ScriptDir . "\config.json")))
    password := cfg["bravo"]["password"]
}

DumpCombos(root, tag) {
    combos := 0
    try combos := root.FindElements({Type: "ComboBox"})
    D(tag . ": ComboBox count=" . (combos ? combos.Length : 0))
    if combos {
        for idx, c in combos {
            aid := "", nm := "", y := ""
            try aid := c.AutomationId
            try nm := c.Name
            try y := c.BoundingRectangle.t
            items := ""
            try {
                c.ExpandCollapsePattern.Expand()
                Sleep(450)
                lis := c.FindElements({Type: "ListItem"})
                if lis {
                    for li in lis {
                        ln := ""
                        try ln := li.Name
                        items .= "[" . ln . "]"
                    }
                }
                try c.ExpandCollapsePattern.Collapse()
                Sleep(200)
            }
            D("  combo[" . idx . "] aid='" . aid . "' name='" . nm . "' y=" . y . " items=" . SubStr(items, 1, 400))
        }
    }
}
DumpDates(root) {
    eds := 0
    try eds := root.FindElements({Type: "Edit"})
    D("Edit count=" . (eds ? eds.Length : 0))
    if eds {
        for idx, e in eds {
            aid := "", nm := "", cn := "", y := "", x := ""
            try aid := e.AutomationId
            try nm := e.Name
            try cn := e.LocalizedControlType
            try y := e.BoundingRectangle.t
            try x := e.BoundingRectangle.l
            if (aid != "" || InStr(nm, "Date") || InStr(nm, "BravoDateEdit"))
                D("  edit[" . idx . "] aid='" . aid . "' name='" . nm . "' ctype='" . cn . "' x=" . x . " y=" . y)
        }
    }
}

if !WaitForBravoWindowExists(30) {
    D("FAIL no window")
    FileAppend("FAIL no-window", IRES, "UTF-8")
    ExitApp
}
ActivateBravo()
DismissPopups()
if !EnsureStore("WAY", password) {
    D("FAIL ensure WAY")
    FileAppend("FAIL ensure", IRES, "UTF-8")
    ExitApp
}
Loop 4 {
    try {
        if ClickByName("Cancel", 1200)
            Sleep(900)
        else
            break
    } else break
}
BackToDashboard()
Sleep(800)
DismissPopups()

try {
    D("open Void/View Transactions")
    ClickByName("Void/View Transactions", 8000)
    Sleep(1500)
    DismissPopups()
    D("click Custom Reports")
    ClickByName("Custom Reports", 5000)
    Sleep(2500)

    root := GetBravoRoot()
    DumpCombos(root, "BEFORE-SELECT")

    ; find + select the saved-report combo via the item itself (robust)
    combos := root.FindElements({Type: "ComboBox"})
    selected := false
    if combos {
        for idx, c in combos {
            try {
                c.ExpandCollapsePattern.Expand()
                Sleep(500)
                li := 0
                try li := c.FindElement({Type: "ListItem", Name: "Claude NICS Transfers"})
                if li {
                    try li.SelectionItemPattern.Select()
                    catch
                        li.Click("left")
                    D("SELECTED 'Claude NICS Transfers' from combo idx=" . idx . " aid='" . c.AutomationId . "'")
                    FileAppend("SAVED-REPORT-COMBO aid='" . c.AutomationId . "' idx=" . idx . "`r`n", IRES, "UTF-8")
                    selected := true
                    Sleep(1500)
                    break
                } else {
                    try c.ExpandCollapsePattern.Collapse()
                }
            }
        }
    }
    if !selected {
        D("WARN: saved-report combo not found by item match")
        FileAppend("WARN saved-report combo not found`r`n", IRES, "UTF-8")
    }

    Sleep(1500)
    root := GetBravoRoot()
    DumpCombos(root, "AFTER-SELECT")
    DumpDates(root)

    ; identify the fee-type combo (item 'NICS Fee')
    combos := root.FindElements({Type: "ComboBox"})
    if combos {
        for idx, c in combos {
            try {
                c.ExpandCollapsePattern.Expand()
                Sleep(400)
                li := 0
                try li := c.FindElement({Type: "ListItem", Name: "NICS Fee"})
                try c.ExpandCollapsePattern.Collapse()
                if li {
                    D("FEE-TYPE combo idx=" . idx . " aid='" . c.AutomationId . "' contains 'NICS Fee'")
                    FileAppend("FEE-TYPE-COMBO aid='" . c.AutomationId . "' idx=" . idx . "`r`n", IRES, "UTF-8")
                }
            }
        }
    }
    FileAppend("DONE`r`n", IRES, "UTF-8")
} catch as e {
    D("ERROR: " . e.Message)
    try FileAppend("ERROR " . e.Message, IRES, "UTF-8")
}

Loop 3 {
    try {
        if ClickByName("Cancel", 1500)
            Sleep(900)
        else break
    } else break
}
D("=== done ===")
ExitApp
