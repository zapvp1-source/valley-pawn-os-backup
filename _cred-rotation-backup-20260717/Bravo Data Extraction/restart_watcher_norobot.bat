@echo off
REM Restart bravo_watcher.ahk in-place using #SingleInstance Force semantics.
REM Just launching a fresh instance is enough — the new AHK process tells
REM the old one to exit and takes over.

cd /d "Y:\Documents\Claude\Projects\Bravo Data Extraction"
start "" "C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe" "bravo_watcher.ahk"
echo done > "Y:\Documents\Claude\Projects\Bravo Data Extraction\logs\restart_watcher.last_run.txt"
