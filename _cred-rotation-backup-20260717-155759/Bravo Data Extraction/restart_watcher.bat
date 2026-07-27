@echo off
REM Restart bravo_watcher.ahk cleanly.
REM
REM Behavior change 2026-05-28:
REM  - Pre-kill ALL AutoHotkey64.exe processes before launching a fresh one.
REM  - #SingleInstance Force is supposed to handle this, but it does NOT kill
REM    instances running in a different Windows session (e.g. an old SYSTEM-
REM    session watcher spawned by the scheduled-task relaunch trick). Without
REM    the pre-kill, multiple watchers accumulated and the stale one with
REM    out-of-date REPORT_HANDLERS would claim triggers and fail them.
REM  - taskkill /F /IM is safe: only this project uses AHK on this machine.

cd /d "Y:\Documents\Claude\Projects\Bravo Data Extraction"

REM Kill any existing AHK processes (no error if none).
taskkill /F /IM AutoHotkey64.exe >nul 2>&1

REM Brief settle, then launch the fresh watcher in the current user session.
timeout /t 2 /nobreak >nul
start "" "C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe" "bravo_watcher.ahk"

REM Stamp the run so we can confirm the bat fired.
echo done %DATE% %TIME% > "Y:\Documents\Claude\Projects\Bravo Data Extraction\logs\restart_watcher.last_run.txt"
