#Requires AutoHotkey v2.0
SetWorkingDir(A_ScriptDir)
#Include lib\Json.ahk
#Include lib\Bravo.ahk

global BRAVO_LOG_PATH := A_ScriptDir . "\logs\bravo_selfheal_2026-05-24.log"
LogMessage("=== self-heal start " . FormatTime(, "yyyy-MM-dd HH:mm:ss") . " ===")

cfgFile := FileRead(A_ScriptDir . "\config.json")
cfg := Json.Load(&cfgFile)
username := cfg["bravo"]["username"]
password := cfg["bravo"]["password"]
LogMessage("  config user=" . username)

; Step 1: ensure Bravo window exists. If not, launch via .appref-ms.
if !WinExist(BRAVO_WIN_TITLE) {
    LogMessage("  no Bravo window; launching via shortcut")
    Run('cmd.exe /c start "" "C:\Users\joshuadavis\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Bravo Store Systems\Bravo.appref-ms"', , "Hide")
    LogMessage("  waiting up to 120s for Bravo window")
    deadline := A_TickCount + 120000
    while (A_TickCount < deadline) {
        if WinExist(BRAVO_WIN_TITLE)
            break
        Sleep 1000
    }
}

if !WinExist(BRAVO_WIN_TITLE) {
    LogMessage("  FAIL: Bravo window never appeared")
    FileAppend("FAIL_NO_WINDOW", A_ScriptDir . "\logs\bravo_selfheal_result.txt")
    ExitApp
}

WinActivate(BRAVO_WIN_TITLE)
Sleep 800
title := WinGetTitle(BRAVO_WIN_TITLE)
LogMessage("  current title: '" . title . "'")

if InStr(title, "VALLEY PAWN - ") {
    LogMessage("  already on Dashboard: " . title)
    FileAppend("OK_ALREADY:" . title, A_ScriptDir . "\logs\bravo_selfheal_result.txt")
    ExitApp
}

; Step 2: if login screen, recover via existing helper.
LogMessage("  not on Dashboard, trying RecoverFromAutoLock")
if RecoverFromAutoLock(password) {
    Sleep 1500
    title := WinGetTitle(BRAVO_WIN_TITLE)
    LogMessage("  post-recover title: '" . title . "'")
    if InStr(title, "VALLEY PAWN - ") {
        FileAppend("OK_LOGGED_IN:" . title, A_ScriptDir . "\logs\bravo_selfheal_result.txt")
        ExitApp
    }
}

; Step 3: wait again in case there is a slow update / splash.
LogMessage("  waiting another 60s for dashboard title")
if WaitForBravoReady(60) {
    title := WinGetTitle(BRAVO_WIN_TITLE)
    LogMessage("  ready: '" . title . "'")
    FileAppend("OK_DELAYED:" . title, A_ScriptDir . "\logs\bravo_selfheal_result.txt")
    ExitApp
}

title := WinGetTitle(BRAVO_WIN_TITLE)
LogMessage("  FAIL: title still '" . title . "'")
FileAppend("FAIL_STUCK:" . title, A_ScriptDir . "\logs\bravo_selfheal_result.txt")
ExitApp

