# _scrap_closeout_launch.ps1 — one-shot launcher for ScrapBucketCloseoutWatcher.ahk (added 2026-09-28).
# Invoked from the Mac host by Valley Pawn OS/bin/scrap_closeout_run.sh via prlctl (Session 0), so it uses
# the same scheduled-task trick as _relaunch_bravo_and_watcher.ps1 to spawn the AHK process in the
# interactive Session 1 (UIA automation only works there). Kills any previous scrap watcher first
# (CommandLine match only — never a blanket AutoHotkey64 kill; the main pipeline watcher is untouched).
$ErrorActionPreference = 'Continue'
$user = "joshuadavis"
$ahk  = "C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe"
$root = "Y:\Documents\Claude\Projects\Bravo Data Extraction"
if (-not (Test-Path "$root\ScrapBucketCloseoutWatcher.ahk")) { $root = "\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction" }

Get-CimInstance Win32_Process -Filter "Name='AutoHotkey64.exe'" | ForEach-Object {
    if ($_.CommandLine -like '*ScrapBucketCloseoutWatcher.ahk*') {
        Write-Output ("stopping previous scrap watcher PID=" + $_.ProcessId)
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
}
Start-Sleep -Seconds 2

$taskName = "ClaudeScrapCloseoutLaunch"
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
$action    = New-ScheduledTaskAction -Execute $ahk -Argument ('"' + $root + '\ScrapBucketCloseoutWatcher.ahk"')
$trigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
Start-Sleep -Seconds 8

$alive = $false
Get-CimInstance Win32_Process -Filter "Name='AutoHotkey64.exe'" | ForEach-Object {
    if ($_.CommandLine -like '*ScrapBucketCloseoutWatcher.ahk*') {
        $sid = (Get-Process -Id $_.ProcessId -ErrorAction SilentlyContinue).SessionId
        Write-Output ("scrap watcher PID=" + $_.ProcessId + " SessionId=" + $sid + " root=" + $root)
        $alive = $true
    }
}
if ($alive) { Write-Output "LAUNCHED_OK" } else { Write-Output "LAUNCH_FAILED" }
