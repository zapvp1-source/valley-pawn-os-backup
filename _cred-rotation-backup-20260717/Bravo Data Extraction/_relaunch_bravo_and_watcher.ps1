# Launch Bravo + relaunch the watcher in the user's interactive Session 1.
# Uses the scheduled-task -> Start-ScheduledTask trick so the processes
# spawn in Session 1 even though we are invoked from Session 0 via prlctl.

$ErrorActionPreference = 'Continue'
$user = "joshuadavis"
$root = "\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction"

function Spawn-InSession1 {
    param($taskName, $execPath, $argString)
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    $action    = New-ScheduledTaskAction -Execute $execPath -Argument $argString
    $trigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
    $principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
    $settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
    Start-ScheduledTask -TaskName $taskName
}

# --- Step 1: Launch Bravo via .appref-ms shortcut --------------------------
Write-Host "=== Launching Bravo ==="
$bravoShortcut = "C:\Users\joshuadavis\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Bravo Store Systems\Bravo.appref-ms"
Spawn-InSession1 -taskName "ClaudeBravoLaunch" -execPath "cmd.exe" -argString ('/c start "" "' + $bravoShortcut + '"')
Start-Sleep -Seconds 30

$bravoProcs = Get-Process -Name "Bravo*" -ErrorAction SilentlyContinue
if ($bravoProcs) {
    foreach ($p in $bravoProcs) { Write-Host ("Bravo PID=" + $p.Id + " SessionId=" + $p.SessionId + " Name=" + $p.ProcessName) }
} else {
    Write-Host "WARN: Bravo not visible in tasklist yet (ClickOnce dfsvc may still be launching it)"
}

# --- Step 2: Relaunch watcher (replaces old via #SingleInstance Force) -----
Write-Host "=== Relaunching watcher ==="
$ahk = "C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe"
$watcher = '"' + $root + '\bravo_watcher.ahk"'
Spawn-InSession1 -taskName "ClaudeBravoWatcherLaunch" -execPath $ahk -argString $watcher
Start-Sleep -Seconds 10

$ahkProcs = Get-Process -Name AutoHotkey64 -ErrorAction SilentlyContinue
foreach ($p in $ahkProcs) {
    $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId=$($p.Id)").CommandLine
    Write-Host ("AHK PID=" + $p.Id + " SessionId=" + $p.SessionId + " CMD=" + $cmd)
}

# --- Step 3: Cleanup -------------------------------------------------------
Unregister-ScheduledTask -TaskName "ClaudeBravoLaunch" -Confirm:$false -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName "ClaudeBravoWatcherLaunch" -Confirm:$false -ErrorAction SilentlyContinue

Write-Host "=== Done ==="
