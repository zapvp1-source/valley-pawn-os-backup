# Launch _uia_nics_recon.ahk in joshuadavis Session 1 (interactive), mapping Y:
# first (same proven technique as _run_inspect.ps1). READ-ONLY recon.

$mapTaskName = 'ClaudeMapYRecon'
Unregister-ScheduledTask -TaskName $mapTaskName -Confirm:$false -ErrorAction SilentlyContinue
$mapAction    = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument '/c net use Y: \\Mac\Home /persistent:yes'
$mapTrigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$mapPrincipal = New-ScheduledTaskPrincipal -UserId 'joshuadavis' -LogonType Interactive -RunLevel Limited
$mapSettings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $mapTaskName -Action $mapAction -Trigger $mapTrigger -Principal $mapPrincipal -Settings $mapSettings -Force | Out-Null
Start-ScheduledTask -TaskName $mapTaskName
Start-Sleep -Seconds 4
Unregister-ScheduledTask -TaskName $mapTaskName -Confirm:$false -ErrorAction SilentlyContinue

$taskName = 'ClaudeNicsRecon'
$ahk      = 'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe'
$arg      = '"Y:\Documents\Claude\Projects\Bravo Data Extraction\_uia_nics_recon.ahk"'
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
$action    = New-ScheduledTaskAction -Execute $ahk -Argument $arg
$trigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$principal = New-ScheduledTaskPrincipal -UserId 'joshuadavis' -LogonType Interactive -RunLevel Limited
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
Start-Sleep 5
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
Write-Host "nics recon launched (Y: mapped)"
