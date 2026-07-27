#Requires AutoHotkey v2.0
#SingleInstance Off
#Include lib\Json.ahk
#Include lib\Bravo.ahk
global CONFIG := Map()
CONFIG["paths.logs"] := A_ScriptDir . "\logs"
InitLog(CONFIG["paths.logs"], FormatTime(,"yyyy-MM-ddTHH-mm-ss") . "_probead")
global RES := CONFIG["paths.logs"] . "\_probead_result.txt"
try FileDelete(RES)
ActivateBravo()
Sleep(700)
found := ""
for nm in ["Continue","Close","Skip","No Thanks","Maybe Later","Dismiss","X","OK","Got it","Get Started","Reports","Cancel","Done","Next","Learn More","Shop Now","Remind Me Later","Go to Dashboard","Dashboard","Not Now","Later","Proceed","Enter","Sign In","Submit","Global Access"] {
    ex := false
    try ex := ExistsByName(nm)
    LogMessage("exists '" . nm . "' = " . (ex ? "YES" : "no"))
    if ex
        found .= nm . " | "
}
try FileAppend("FOUND: " . found, RES, "UTF-8")
ExitApp
