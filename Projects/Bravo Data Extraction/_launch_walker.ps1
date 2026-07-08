$taskName = "ClaudeBravoWalkerLaunch"
$ahk      = "C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe"
$script   = '"\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\walk_open_inventory_grid.ahk"'

Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

$action    = New-ScheduledTaskAction -Execute $ahk -Argument $script
$trigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$principal = New-ScheduledTaskPrincipal -UserId "joshuadavis" -LogonType Interactive -RunLevel Limited
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Write-Host ("Task registered: " + $taskName)
Start-ScheduledTask -TaskName $taskName
Write-Host "Walker started"
Start-Sleep -Seconds 6

$procs = Get-Process AutoHotkey64 -ErrorAction SilentlyContinue
foreach ($p in $procs) {
    $cmd = (Get-WmiObject Win32_Process -Filter "ProcessId=$($p.Id)").CommandLine
    Write-Host ("PID=" + $p.Id + " SessionID=" + $p.SessionId + " CMD=" + $cmd)
}

Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
Write-Host "Cleaned up task"
