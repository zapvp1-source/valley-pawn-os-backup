; ============================================================================
; nics_combo_diag.ahk  —  one-shot UIA inspection of the Void/View Transactions
; Custom Reports dialog, to identify the SAVED-REPORT dropdown reliably
; (by AutomationId + which combo's item list contains "Claude NICS Transfers")
; instead of the flaky "bottom-most combo" heuristic.
;
; Run in Session 1 when the pipeline is idle. Writes a plain dump to
; logs\nics_combo_diag.log and a one-line verdict to logs\nics_combo_diag_result.txt.
; Read-only intent: it opens the dialog, enumerates combos + their items, then
; Cancels out. Does NOT run the report or change anything.
; ============================================================================
#Requires AutoHotkey v2.0
SetWorkingDir(A_ScriptDir)
#Include lib\Json.ahk
#Include lib\Bravo.ahk

global DIAG_LOG := A_ScriptDir . "\logs\nics_combo_diag.log"
global DIAG_RES := A_ScriptDir . "\logs\nics_combo_diag_result.txt"
D(msg) {
    global DIAG_LOG
    try FileAppend(FormatTime(, "HH:mm:ss") . "  " . msg . "`r`n", DIAG_LOG, "UTF-8")
}
try FileDelete(DIAG_LOG)
try FileDelete(DIAG_RES)
D("=== nics_combo_diag start ===")

password := ""
try {
    cfg := Json.Load(&(FileRead(A_ScriptDir . "\config.json")))
    password := cfg["bravo"]["password"]
}

if !WaitForBravoWindowExists(30) {
    D("FAIL: no Bravo window")
    FileAppend("FAIL no-window", DIAG_RES, "UTF-8")
    ExitApp
}
ActivateBravo()
DismissPopups()
if !EnsureStore("ROA", password) {
    D("FAIL: EnsureStore ROA")
    FileAppend("FAIL ensure-store", DIAG_RES, "UTF-8")
    ExitApp
}
; clear any stranded editor, then back to dashboard
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
    ; Enumerate every ComboBox-like element: log Type, Name, AutomationId, Y.
    combos := root.FindElements({Type: "ComboBox"})
    D("ComboBox count = " . (combos ? combos.Length : 0))
    targetIdx := 0
    if combos {
        for idx, c in combos {
            aid := "", nm := "", y := ""
            try aid := c.AutomationId
            try nm := c.Name
            try y := c.BoundingRectangle.t
            D("combo[" . idx . "] aid='" . aid . "' name='" . nm . "' y=" . y)
            ; Try to read its items without committing a selection: expand, enumerate, collapse.
            items := ""
            try {
                c.ExpandCollapsePattern.Expand()
                Sleep(600)
                lis := c.FindElements({Type: "ListItem"})
                if lis {
                    for li in lis {
                        lin := ""
                        try lin := li.Name
                        items .= "[" . lin . "]"
                        if InStr(lin, "Claude NICS Transfers")
                            targetIdx := idx
                    }
                }
                try c.ExpandCollapsePattern.Collapse()
                Sleep(300)
            } catch as e {
                D("    (could not enumerate items: " . e.Message . ")")
            }
            if (items != "")
                D("    items=" . SubStr(items, 1, 500))
        }
    }
    if (targetIdx > 0) {
        tc := combos[targetIdx]
        taid := "", tname := "", ty := ""
        try taid := tc.AutomationId
        try tname := tc.Name
        try ty := tc.BoundingRectangle.t
        D("VERDICT: saved-report combo is index " . targetIdx . " aid='" . taid . "' name='" . tname . "' y=" . ty)
        FileAppend("OK idx=" . targetIdx . " aid='" . taid . "' name='" . tname . "' y=" . ty, DIAG_RES, "UTF-8")
    } else {
        D("VERDICT: no combo contained 'Claude NICS Transfers'")
        FileAppend("NO-MATCH (see log; report may need scrolling or different module state)", DIAG_RES, "UTF-8")
    }
} catch as e {
    D("ERROR: " . e.Message)
    try FileAppend("ERROR " . e.Message, DIAG_RES, "UTF-8")
}

; clean exit
Loop 3 {
    try {
        if ClickByName("Cancel", 1500)
            Sleep(900)
        else break
    } else break
}
D("=== done ===")
ExitApp
