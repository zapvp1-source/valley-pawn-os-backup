#Requires AutoHotkey v2.0
#SingleInstance Off
#Include lib\Json.ahk
#Include lib\Bravo.ahk
global CONFIG := Map()
CONFIG["paths.logs"] := A_ScriptDir . "\logs"
InitLog(CONFIG["paths.logs"], FormatTime(,"yyyy-MM-ddTHH-mm-ss") . "_dismissad")
global RES := CONFIG["paths.logs"] . "\_dismissad_result.txt"
try FileDelete(RES)
ActivateBravo()
Sleep(700)
DismissPopups()
clicked := "none"
try {
    ClickByName("Close", 4000)
    clicked := "Close"
}
Sleep(2500)
DismissPopups()
onDash := FindByName("Reports", 8000) ? "yes" : "no"
try FileAppend("clicked=" . clicked . " onDash=" . onDash . " code=" . GetCurrentStoreCode() . " onLogin=" . (IsOnLoginScreen()?"yes":"no"), RES, "UTF-8")
ExitApp
