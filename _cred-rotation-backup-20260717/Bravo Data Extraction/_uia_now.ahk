#Requires AutoHotkey v2.0
SetWorkingDir(A_ScriptDir)
#Include lib\UIA-v2\UIA.ahk
out := A_ScriptDir . "\logs\_uia_now.txt"
try FileDelete(out)
hwnd := WinExist("Bravo ")
if !hwnd {
    FileAppend("NO_WINDOW", out)
    ExitApp
}
root := UIA.ElementFromHandle(hwnd)
s := "TITLE: " . WinGetTitle("Bravo ") . "`n`n"
try {
    for el in root.FindAll({Type:"Button"})
        s .= "BUTTON: '" . el.Name . "'`n"
} catch as e
    s .= "btn err: " . e.Message . "`n"
try {
    for el in root.FindAll({Type:"Text"})
        if (Trim(el.Name) != "")
            s .= "TEXT: '" . el.Name . "'`n"
} catch as e
    s .= "txt err: " . e.Message . "`n"
try {
    for el in root.FindAll({Type:"Edit"})
        s .= "EDIT: '" . el.Name . "' val='" . el.Value . "'`n"
} catch as e
    s .= "edit err: " . e.Message . "`n"
try {
    for el in root.FindAll({Type:"ListItem"})
        s .= "LISTITEM: '" . el.Name . "'`n"
} catch as e
    s .= "li err: " . e.Message . "`n"
try {
    for el in root.FindAll({Type:"Hyperlink"})
        s .= "LINK: '" . el.Name . "'`n"
} catch as e
    s .= "link err: " . e.Message . "`n"
FileAppend(s, out)
ExitApp
