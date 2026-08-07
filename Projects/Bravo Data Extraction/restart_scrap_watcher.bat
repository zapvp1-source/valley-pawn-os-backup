@echo off
REM Restart ScrapBucketCloseoutWatcher.ahk cleanly.
REM Kills ONLY the AutoHotkey64.exe process(es) whose command line
REM references ScrapBucketCloseoutWatcher.ahk - deliberately NOT a blanket
REM "taskkill /IM AutoHotkey64.exe" like restart_watcher.bat uses, because
REM this machine now runs TWO AHK processes (the main pipeline watcher and
REM this scrap closeout watcher) and a blanket kill here would take down
REM the main pipeline as an unintended side effect.

cd /d "Y:\Documents\Claude\Projects\Bravo Data Extraction"

for /f "tokens=2 delims=," %%P in ('wmic process where "name='AutoHotkey64.exe' and CommandLine like '%%ScrapBucketCloseoutWatcher.ahk%%'" get ProcessId /format:csv ^| findstr /r "[0-9]"') do (
    taskkill /F /PID %%P >nul 2>&1
)

timeout /t 2 /nobreak >nul
start "" "C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe" "ScrapBucketCloseoutWatcher.ahk"

echo done %DATE% %TIME% > "Y:\Documents\Claude\Projects\Bravo Data Extraction\logs-scrap\restart_scrap_watcher.last_run.txt"
