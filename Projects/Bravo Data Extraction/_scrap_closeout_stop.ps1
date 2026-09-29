# _scrap_closeout_stop.ps1 — stop ScrapBucketCloseoutWatcher.ahk after a one-shot run (added 2026-09-28)
# and make sure the main pipeline watchdog is back on (the handler's ResumeMainWatcher does this too;
# this is the belt-and-braces copy so a crashed run can never leave the pipeline paused).
$ErrorActionPreference = 'Continue'
Get-CimInstance Win32_Process -Filter "Name='AutoHotkey64.exe'" | ForEach-Object {
    if ($_.CommandLine -like '*ScrapBucketCloseoutWatcher.ahk*') {
        Write-Output ("stopping scrap watcher PID=" + $_.ProcessId)
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
}
Unregister-ScheduledTask -TaskName "ClaudeScrapCloseoutLaunch" -Confirm:$false -ErrorAction SilentlyContinue
schtasks /change /tn BravoWatcherWatchdog /enable | Out-Null
schtasks /run /tn BravoWatcherWatchdog | Out-Null
Start-Sleep -Seconds 3
$main = $false
Get-CimInstance Win32_Process -Filter "Name='AutoHotkey64.exe'" | ForEach-Object {
    if ($_.CommandLine -like '*bravo_watcher.ahk*') { $main = $true; Write-Output ("main watcher PID=" + $_.ProcessId) }
}
Write-Output ("main watcher running: " + $main)
Write-Output "STOPPED_OK"
