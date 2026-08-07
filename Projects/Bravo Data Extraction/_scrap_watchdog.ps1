# _scrap_watchdog.ps1 - self-healing monitor for ScrapBucketCloseoutWatcher.ahk
# Registered in Windows Task Scheduler as "ScrapCloseoutWatcherWatchdog".
# Mirrors _watchdog.ps1's alive-check/restart pattern for the main pipeline
# watcher, but targets ScrapBucketCloseoutWatcher.ahk specifically by
# matching the running process's own CommandLine - NOT just image name,
# because restart_watcher.bat (owned by the EXISTING BravoWatcherWatchdog
# task, never modified by this build) does `taskkill /F /IM AutoHotkey64.exe`
# unconditionally whenever IT detects a hang. That kills every AutoHotkey64
# process on the machine, including this scrap watcher, as a side effect.
# This watchdog's job is specifically to notice that collateral kill and
# bring the scrap watcher back - it does not touch the main pipeline watcher
# at all (RunScrapCloseoutManifest already handles pausing/resuming that one
# itself, only for the duration of an actual bucket-close run).
#
# SHIPPED DISABLED - see setup_scrap_watcher.bat. Enable only after one
# supervised live test of a real manifest.

$root = 'Y:\Documents\Claude\Projects\Bravo Data Extraction'
if (-not (Test-Path $root)) { $root = '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction' }
$log = Join-Path $root 'logs-scrap\scrap_watchdog.log'
$stamp = Join-Path $root 'logs-scrap\scrap_watchdog.last_restart.txt'
function Log($m) { ("{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m) | Add-Content $log }

$alive = $false
Get-Process AutoHotkey64 -ErrorAction SilentlyContinue | ForEach-Object {
    $cmd = (Get-WmiObject Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine
    if ($cmd -like '*ScrapBucketCloseoutWatcher.ahk*') { $alive = $true }
}

if ($alive) { exit 0 }   # healthy - stay quiet

# Throttle: at most one restart per 5 min, so a genuinely crash-looping
# script doesn't spam relaunches.
if (Test-Path $stamp) {
    if (((Get-Date) - (Get-Item $stamp).LastWriteTime).TotalMinutes -lt 5) {
        Log "not running, but throttled (restarted <5min ago)"
        exit 0
    }
}

Log "RESTART: ScrapBucketCloseoutWatcher.ahk not found among running AutoHotkey64 processes"
Get-Date -Format 'yyyy-MM-dd HH:mm:ss' | Set-Content $stamp
& (Join-Path $root 'restart_scrap_watcher.bat') *>> $log
Log "restart script finished"
