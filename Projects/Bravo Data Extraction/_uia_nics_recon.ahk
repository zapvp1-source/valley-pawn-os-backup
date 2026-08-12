#Requires AutoHotkey v2.0
; Measure the OPEN date calendar popup: the End-date field rect, the month
; header (to confirm displayed month), and the arrow Buttons near the header
; row — so we can compute the correct ► (next) arrow X offset for THIS dialog.
SetWorkingDir(A_ScriptDir)
#Include lib\UIA-v2\UIA.ahk

out := A_ScriptDir . "\logs\_uia_cal.txt"
try FileDelete(out)
s := "CAL RECON " . A_Now . "`n"
hwnd := WinExist("Bravo ")
if !hwnd {
    FileAppend("NO_WINDOW", out)
    ExitApp
}
root := UIA.ElementFromHandle(hwnd)

; report date fields (empty aid BravoDateEdit) for reference
try {
    for e in root.FindAll({Type: "Edit"}) {
        nm := ""
        try nm := e.Name
        if (nm != "BravoDateEdit")
            continue
        aid := ""
        try aid := e.AutomationId
        if (aid != "")
            continue
        val := "", r := ""
        try val := e.Value
        try {
            b := e.BoundingRectangle
            r := b.l . "," . b.t . "," . b.r . "," . b.b
        }
        s .= "DATEFIELD val='" . val . "' rect=[" . r . "]`n"
    }
}

desk := UIA.GetRootElement()

s .= "`n=== month header (matching 'Month YYYY') ===`n"
for t in ["Text", "Button", "Header"] {
    try {
        for e in desk.FindAll({Type: t}) {
            nm := ""
            try nm := e.Name
            if RegExMatch(nm, "i)^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}$") {
                r := ""
                try {
                    b := e.BoundingRectangle
                    r := b.l . "," . b.t . "," . b.r . "," . b.b
                }
                s .= "HEADER[" . t . "] '" . nm . "' rect=[" . r . "]`n"
            }
        }
    }
}

s .= "`n=== Buttons in calendar region (cy 830-1030, cx 1300-2300) ===`n"
try {
    for e in desk.FindAll({Type: "Button"}) {
        nm := "", r := "", cy := 0, cx := 0
        try nm := e.Name
        try {
            b := e.BoundingRectangle
            cy := b.t + (b.b - b.t) // 2
            cx := b.l + (b.r - b.l) // 2
            r := b.l . "," . b.t . "," . b.r . "," . b.b
        }
        if (cy > 830 && cy < 1030 && cx > 1300 && cx < 2300)
            s .= "BTN '" . nm . "' center=(" . cx . "," . cy . ") rect=[" . r . "]`n"
    }
}
FileAppend(s, out)
ExitApp
