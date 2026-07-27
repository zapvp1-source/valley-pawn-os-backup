@echo off
cd /d "Y:\Documents\Claude\Projects\Bravo Data Extraction"
powershell -ExecutionPolicy Bypass -File "Y:\Documents\Claude\Projects\Bravo Data Extraction\_restart_watcher.ps1"
echo done > "Y:\Documents\Claude\Projects\Bravo Data Extraction\logs\_claude_restart_done.txt"
