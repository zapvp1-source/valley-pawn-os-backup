
$taskName = "ClaudeBravoWatcherLaunch"
$ahk      = "C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe"
$watcher  = '"\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\bravo_watcher.ahk"'

# Clean up any prior version
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

# Build task pieces
$action    = New-ScheduledTaskAction -Execute $ahk -Argument $watcher
$trigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))   # placeholder; we Start it manually
$principal = New-ScheduledTaskPrincipal -UserId "joshuadavis" -LogonType Interactive -RunLevel Limited
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Write-Host ("Task registered: " + $taskName)

# Fire it
Start-ScheduledTask -TaskName $taskName
Write-Host "Task started"

# Give it a few seconds
Start-Sleep -Seconds 6

# Show all AutoHotkey64.exe processes with session IDs
Write-Host ""
Write-Host "=== AutoHotkey64.exe processes ==="
$procs = Get-Process AutoHotkey64 -ErrorAction SilentlyContinue
foreach ($p in $procs) {
    $cmd = (Get-WmiObject Win32_Process -Filter "ProcessId=$($p.Id)").CommandLine
    Write-Host ("PID=" + $p.Id + " SessionID=" + $p.SessionId + " CMD=" + $cmd)
}

# Clean up the scheduled task entry (the launched process is now independent)
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
Write-Host ("Cleaned up task: " + $taskName)
