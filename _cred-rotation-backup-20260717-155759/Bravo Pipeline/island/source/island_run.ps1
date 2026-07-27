# island_run.ps1 — map Y: in the interactive session FIRST (per _restart_watcher.ps1),
# then launch the island grid-read AHK via a one-shot Scheduled Task, direct-execute.
$taskName = "ClaudeIslandGridread"
$ahk      = "C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe"
$script   = '"Y:\Documents\Claude\Projects\Bravo Pipeline\island\source\Loans75_gridread_island.ahk"'

# Kill only the prior ISLAND AHK (match script name — never the watcher)
Get-Process AutoHotkey64 -ErrorAction SilentlyContinue | Where-Object {
    ((Get-WmiObject Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine) -like "*Loans75_gridread_island*"
} | ForEach-Object { Stop-Process -Id $_.Id -Force }

# --- Map Y: in joshuadavis's interactive session (the missing step) ----------
$mapTaskName = "ClaudeIslandMapY"
Unregister-ScheduledTask -TaskName $mapTaskName -Confirm:$false -ErrorAction SilentlyContinue
$mapAction    = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument '/c net use Y: \\Mac\Home /persistent:yes'
$mapTrigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$mapPrincipal = New-ScheduledTaskPrincipal -UserId "joshuadavis" -LogonType Interactive -RunLevel Limited
$mapSettings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $mapTaskName -Action $mapAction -Trigger $mapTrigger -Principal $mapPrincipal -Settings $mapSettings -Force | Out-Null
Start-ScheduledTask -TaskName $mapTaskName
Start-Sleep -Seconds 4
Unregister-ScheduledTask -TaskName $mapTaskName -Confirm:$false -ErrorAction SilentlyContinue

# --- Launch the island AHK ---------------------------------------------------
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
$action    = New-ScheduledTaskAction -Execute $ahk -Argument $script
$trigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$principal = New-ScheduledTaskPrincipal -UserId "joshuadavis" -LogonType Interactive -RunLevel Limited
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances Parallel
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
Start-Sleep -Seconds 2
$info = Get-ScheduledTaskInfo -TaskName $taskName
Write-Host ("island task started; LastTaskResult=" + $info.LastTaskResult)
