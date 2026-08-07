@echo off
REM One-time setup: registers the ScrapCloseoutWatcherWatchdog scheduled
REM task. Mirrors how BravoWatcherWatchdog is set up (a "run every N
REM minutes" task that both launches the watcher on first fire, since it
REM isn't alive yet, and relaunches it if it dies afterward).
REM
REM SHIPS DISABLED ON PURPOSE. This build has not yet had a supervised
REM live test against a real Bravo bucket via this AHK path (only via
REM manual computer-use, 2026-08-05/06). Before enabling:
REM   1. Drop one real manifest into triggers-scrap\
REM   2. Manually run: AutoHotkey64.exe ScrapBucketCloseoutWatcher.ahk
REM      with the VM screen visible, watch it process that one manifest
REM   3. Confirm results-scrap\<id>.result.json shows verified=true for
REM      every bucket AND the amounts match Bravo's own bucket status
REM   4. Only then: schtasks /change /tn ScrapCloseoutWatcherWatchdog /enable

cd /d "Y:\Documents\Claude\Projects\Bravo Data Extraction"

schtasks /create /tn ScrapCloseoutWatcherWatchdog ^
    /tr "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File \"Y:\Documents\Claude\Projects\Bravo Data Extraction\_scrap_watchdog.ps1\"" ^
    /sc minute /mo 2 /ru joshuadavis /it /f

schtasks /change /tn ScrapCloseoutWatcherWatchdog /disable

echo Task created and DISABLED. Enable with:
echo   schtasks /change /tn ScrapCloseoutWatcherWatchdog /enable
echo after a supervised live test. See this file's header comment.
