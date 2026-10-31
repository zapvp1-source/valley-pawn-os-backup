# _run_whatsnew.ps1 -- launch _whatsnew_dismiss.ahk (cloned from _run_bravomapper.ps1, 2026-10-30) in joshuadavis Session 1 (additive, 2026-09-30).
# Same proven scheduled-task technique as _run_inspect.ps1 / _restart_watcher.ps1:
# map Y: in the interactive session first, then start AHK from Y:\ (never UNC).
# /ErrorStdOut keeps any AHK load error OFF the screen (no modal over Bravo).

$mapTaskName = 'ClaudeMapYDriveWhatsNew'
Unregister-ScheduledTask -TaskName $mapTaskName -Confirm:$false -ErrorAction SilentlyContinue
$mapAction    = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument '/c net use Y: \\Mac\Home /persistent:yes'
$mapTrigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$mapPrincipal = New-ScheduledTaskPrincipal -UserId 'joshuadavis' -LogonType Interactive -RunLevel Limited
$mapSettings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $mapTaskName -Action $mapAction -Trigger $mapTrigger -Principal $mapPrincipal -Settings $mapSettings -Force | Out-Null
Start-ScheduledTask -TaskName $mapTaskName
Start-Sleep -Seconds 4
Unregister-ScheduledTask -TaskName $mapTaskName -Confirm:$false -ErrorAction SilentlyContinue

$taskName = 'ClaudeWhatsNew'
$ahk      = 'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe'
$arg      = '/ErrorStdOut "Y:\Documents\Claude\Projects\Bravo Data Extraction\_whatsnew_dismiss.ahk"'
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
$cmdArg   = '/c ""' + $ahk + '" ' + $arg + ' > "Y:\Documents\Claude\Projects\Bravo Data Extraction\logs\_whatsnew_err.txt" 2>&1"'
$action    = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument $cmdArg
$trigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$principal = New-ScheduledTaskPrincipal -UserId 'joshuadavis' -LogonType Interactive -RunLevel Limited
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
Start-Sleep -Seconds 30
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
Write-Host 'whatsnew launched'
