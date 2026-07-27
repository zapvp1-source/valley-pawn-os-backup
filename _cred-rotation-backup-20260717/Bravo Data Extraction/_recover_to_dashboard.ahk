; Autonomous recovery: from ANY Bravo state reach a REAL store Dashboard
; (verified by the "Reports" sidebar, not just the title bar). Retries the
; login a few times to defeat the flaky promo-login screen. Reuses
; lib/Bravo.ahk + lib/StoreCycle.ahk helpers (in-session focus works).
; Writes logs\_recover_result.txt = "OK <code>" or "FAIL <reason>".
#Requires AutoHotkey v2.0
#SingleInstance Off
#Include lib\Json.ahk
#Include lib\Bravo.ahk
#Include lib\StoreCycle.ahk

global CONFIG := Map()
CONFIG["paths.logs"]     := A_ScriptDir . "\logs"
CONFIG["bravo.username"] := "FREE1@WAY"
CONFIG["bravo.password"] := "Health2035!"
global RES := CONFIG["paths.logs"] . "\_recover_result.txt"
WriteRes(s) {
    global RES
    try FileDelete(RES)
    try FileAppend(s, RES, "UTF-8")
}
InitLog(CONFIG["paths.logs"], FormatTime(, "yyyy-MM-ddTHH-mm-ss") . "_recover")
password := CONFIG["bravo.password"]
target := A_Args.Length >= 1 ? A_Args[1] : "HAR"

LogMessage("=== RECOVER start target=" . target . " ===")
winOk := false
deadline := A_TickCount + 90000
Loop {
    if WinExist("Bravo ") {
        winOk := true
        break
    }
    if (A_TickCount > deadline)
        break
    Sleep(1000)
}
if !winOk {
    WriteRes("FAIL no-window")
    ExitApp(1)
}

Loop 5 {
    attempt := A_Index
    LogMessage("--- attempt " . attempt . " ---")
    ActivateBravo()
    Sleep(700)
    DismissPopups()

    ; REAL dashboard? (Reports sidebar present AND not on login)
    onLogin := IsOnLoginScreen()
    if (!onLogin) {
        if FindByName("Reports", 4000) {
            code := GetCurrentStoreCode()
            LogMessage("on REAL dashboard " . code)
            WriteRes("OK " . code)
            ExitApp(0)
        }
    }

    ; Select Store selector? double-click target store row
    storeName := SC_STORE_FULL_NAME.Has(target) ? SC_STORE_FULL_NAME[target] : ""
    if (storeName != "") {
        cands := [storeName, StrUpper(storeName), target, StrUpper(target)]
        seen := WaitForAnyByName(cands, 3000)
        if (seen != "") {
            LogMessage("selector -> double-click '" . seen . "'")
            try DoubleClickByName(seen, 3000)
            Sleep(2500)
            DismissPopups()
        }
    }

    ; Finish login from the form
    RecoverFromAutoLock(password)
    Sleep(2000)
    DismissPopups()

    ; Verify REAL dashboard (Reports sidebar)
    if FindByName("Reports", 12000) {
        code := GetCurrentStoreCode()
        LogMessage("attempt " . attempt . " reached Reports -> " . code)
        WriteRes("OK " . code)
        ExitApp(0)
    }
    LogMessage("attempt " . attempt . " did not reach Reports (onLogin=" . (IsOnLoginScreen()?"yes":"no") . " code=" . GetCurrentStoreCode() . ")")
    Sleep(2500)
}

WriteRes("FAIL no-dashboard code=" . GetCurrentStoreCode() . " onLogin=" . (IsOnLoginScreen() ? "yes" : "no"))
ExitApp(2)
