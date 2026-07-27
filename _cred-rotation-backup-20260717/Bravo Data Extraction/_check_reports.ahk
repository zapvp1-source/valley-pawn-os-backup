#Requires AutoHotkey v2.0
#SingleInstance Off
#Include lib\Json.ahk
#Include lib\Bravo.ahk
global CONFIG := Map()
CONFIG["paths.logs"] := A_ScriptDir . "\logs"
InitLog(CONFIG["paths.logs"], FormatTime(,"yyyy-MM-ddTHH-mm-ss") . "_chkrep")
global RES := CONFIG["paths.logs"] . "\_chkrep_result.txt"
try FileDelete(RES)
SetTitleMatchMode(2)
try WinRestore("Bravo ")
Sleep(400)
try WinActivate("Bravo ")
Sleep(400)
try WinMaximize("Bravo ")
Sleep(9000)
DismissPopups()
r := FindByName("Reports", 15000) ? "yes" : "no"
try FileAppend("reports=" . r . " code=" . GetCurrentStoreCode() . " onLogin=" . (IsOnLoginScreen()?"yes":"no"), RES, "UTF-8")
ExitApp
