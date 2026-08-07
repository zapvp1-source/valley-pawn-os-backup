; ============================================================================
; ScrapBucketCloseoutWatcher.ahk — persistent poller for scrap bucket
; close-out manifests. Mirrors bravo_watcher.ahk's own polling/claim
; pattern exactly, but runs as a SEPARATE process against a SEPARATE
; trigger folder (triggers-scrap\) so it can never collide with the main
; data-extraction pipeline's own triggers\ folder or dispatch tables.
; Per the project's additive-only rule, this file and everything it
; touches is new - nothing in bravo_watcher.ahk / bravo_export.ahk /
; their dispatch tables is modified.
;
; Trigger file lifecycle:
;   triggers-scrap\<id>.json            (drop an approved manifest here)
;   triggers-scrap\claimed\<id>.json    (moved here atomically once claimed)
;   results-scrap\<id>.result.json      (written when the run finishes)
;   logs-scrap\<id>.log                 (full step-by-step log)
;
; IMPORTANT - first run must be supervised:
;   The bucket close-out sequence in reports/ScrapBucketCloseout.ahk has
;   been verified live via MANUAL computer-use (2026-08-05/06, all 10
;   buckets of the Aug settlement, tied to the wire to the penny) but has
;   NOT yet been exercised end-to-end through this AHK path against a real
;   bucket. Drop one manifest, watch the VM screen while it runs, confirm
;   the result JSON and Bravo's own bucket status agree with expectations,
;   THEN enable ScrapCloseoutWatcherWatchdog for unattended future months.
;   That watchdog task ships DISABLED (see setup_scrap_watcher.bat) until
;   someone flips it on deliberately.
;
; Hotkeys (only active while this script has focus / is the active AHK
; instance - same convention as bravo_watcher.ahk):
;   Ctrl+Alt+Shift+W = exit this watcher cleanly
; ============================================================================
#Requires AutoHotkey v2.0
#SingleInstance Force
Persistent

FileAppend("BOOT START: " . FormatTime(, "yyyy-MM-dd HH:mm:ss") . "`r`n", A_ScriptDir . "\logs-scrap\_diag_boot.log", "UTF-8")

#Include lib\_secrets.ahk
#Include lib\Json.ahk
#Include lib\Bravo.ahk
#Include lib\EnsureDashboard.ahk
#Include lib\StoreCycle.ahk
#Include reports\ScrapRefiningGold.ahk
#Include reports\ScrapBucketCloseout.ahk

FileAppend("BOOT AFTER INCLUDES: " . FormatTime(, "yyyy-MM-dd HH:mm:ss") . "`r`n", A_ScriptDir . "\logs-scrap\_diag_boot.log", "UTF-8")

; ---------------------------------------------------------------------
; Fail() - ScrapRefiningGold.ahk (included above) calls Fail(result,
; started, msg) but that function only lives in reports\SafeRegisterJournal.ahk,
; which this watcher does NOT include (additive-only: we do not pull in
; unrelated report handlers just to satisfy one symbol). Without it, AHK v2's
; load-time static analysis flags Fail as "local variable never assigned"
; and pops a blocking MsgBox on EVERY launch of this script - even though
; PullScrapRefiningGold() is never actually called during a scrap closeout
; run. That dialog has no one to click it during unattended/native launches,
; so the whole watcher hangs forever before Main() even starts. Defining a
; local copy here (identical to SafeRegisterJournal.ahk's) resolves the
; symbol and removes the dialog. Discovered 2026-08-06 during the silver
; bucket closeout test.
Fail(result, started, msg) {
    result["error"] := msg
    result["duration_ms"] := A_TickCount - started
    LogMessage("  ERROR: " . msg)
    return result
}

global CONFIG := Map()
global SCRIPT_DIR := A_ScriptDir
global SCRAP_IS_PROCESSING := false

Main()

Main() {
    global CONFIG, SCRIPT_DIR, BRAVO_PASSWORD

    CONFIG["paths.project_root"]   := SCRIPT_DIR
    CONFIG["paths.triggers_scrap"] := SCRIPT_DIR . "\triggers-scrap"
    CONFIG["paths.scrap_results"]  := SCRIPT_DIR . "\results-scrap"
    CONFIG["paths.logs"]           := SCRIPT_DIR . "\logs-scrap"
    CONFIG["bravo.username"]       := "FREE1@WAY"
    CONFIG["bravo.password"]       := (IsSet(BRAVO_PASSWORD) ? BRAVO_PASSWORD : "Health2080!")
    CONFIG["watcher.poll_interval_ms"] := "60000"

    for key in ["paths.triggers_scrap", "paths.scrap_results", "paths.logs"] {
        dir := CONFIG[key]
        if !DirExist(dir)
            DirCreate(dir)
    }
    claimedDir := CONFIG["paths.triggers_scrap"] . "\claimed"
    if !DirExist(claimedDir)
        DirCreate(claimedDir)

    FileAppend("BOOT BEFORE FIRST POLL: " . FormatTime(, "yyyy-MM-dd HH:mm:ss") . "`r`n", A_ScriptDir . "\logs-scrap\_diag_boot.log", "UTF-8")
    SetTimer(PollScrapTriggers, Integer(CONFIG["watcher.poll_interval_ms"]))
    PollScrapTriggers()
    FileAppend("BOOT AFTER FIRST POLL: " . FormatTime(, "yyyy-MM-dd HH:mm:ss") . "`r`n", A_ScriptDir . "\logs-scrap\_diag_boot.log", "UTF-8")

    markerPath := SCRIPT_DIR . "\logs-scrap\scrap_watcher.last_started.txt"
    try FileDelete(markerPath)
    try FileAppend(
        "Scrap closeout watcher started: " . FormatTime(, "yyyy-MM-dd HH:mm:ss") . "`r`n" .
        "Watching: " . CONFIG["paths.triggers_scrap"] . "`r`n",
        markerPath, "UTF-8"
    )
    TrayTip("Scrap Closeout Watcher started", "Polling " . CONFIG["paths.triggers_scrap"] . " every " . (Integer(CONFIG["watcher.poll_interval_ms"]) / 1000) . "s", 1)
}

PollScrapTriggers() {
    global SCRAP_IS_PROCESSING, CONFIG
    if SCRAP_IS_PROCESSING
        return
    SCRAP_IS_PROCESSING := true
    try {
        dir := CONFIG["paths.triggers_scrap"]
        files := []
        loop files, dir . "\*.json" {
            files.Push(A_LoopFilePath)
        }
        for f in files {
            ProcessScrapTrigger(f)
        }
    } finally {
        SCRAP_IS_PROCESSING := false
    }
}

ProcessScrapTrigger(triggerPath) {
    global CONFIG
    claimedDir := CONFIG["paths.triggers_scrap"] . "\claimed"
    SplitPath(triggerPath, &triggerName)
    claimedPath := claimedDir . "\" . triggerName

    ; Atomic claim - same pattern as bravo_watcher.ahk ProcessTrigger.
    try {
        FileMove(triggerPath, claimedPath, false)
    } catch {
        return  ; lost the race or file vanished; nothing to do
    }

    triggerId := StrReplace(triggerName, ".json", "")
    InitLog(CONFIG["paths.logs"], triggerId)
    LogMessage("=== Scrap closeout trigger claimed: " . claimedPath . " ===")

    try {
        RunScrapCloseoutManifest(claimedPath)
    } catch as e {
        LogMessage("ProcessScrapTrigger: FATAL uncaught error - " . e.Message)
        ; Best-effort: make sure the main watcher isn't left paused if
        ; RunScrapCloseoutManifest died before its own finally block ran.
        try ResumeMainWatcher()
    }
}

; Exit hotkey - mirrors bravo_watcher.ahk's Ctrl+Alt+W convention, shifted
; one modifier so the two watchers never fight over the same hotkey if both
; happen to be running (they normally are: this one plus the main pipeline).
^!+w:: {
    TrayTip("Scrap Closeout Watcher", "Exiting on hotkey", 1)
    ExitApp()
}
