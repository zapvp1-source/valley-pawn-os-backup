#Requires AutoHotkey v2.0
#Include lib\Json.ahk
#Include lib\Bravo.ahk
#Include lib\StoreCycle.ahk
res := "start"
try {
    ActivateBravo()
    Sleep(800)
} catch as e {
    res := "activate-fail:" . e.Message
}
try {
    ClickByName("Done", 6000)
    res := "clicked-Done"
    Sleep(1500)
} catch as e {
    res := "done-fail:" . e.Message
}
FileAppend(res . "`n", "logs\_done_click.txt", "UTF-8")
ExitApp