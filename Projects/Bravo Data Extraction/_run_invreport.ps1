# _run_invreport.ps1 (2026-11-21, eBay Desk) -- clone of _run_mobileevents_goldoff.ps1 launching InvReportBuild.ahk.
# _run_mobileevents.ps1 (2026-11-18, clone of _run_bravomapper.ps1) -- launch InvReportBuild.ahk in joshuadavis Session 1 (additive, 2026-09-30).
# Same proven scheduled-task technique as _run_inspect.ps1 / _restart_watcher.ps1:
# map Y: in the interactive session first, then start AHK from Y:\ (never UNC).
# /ErrorStdOut keeps any AHK load error OFF the screen (no modal over Bravo).
param(
    [string]$Stores = 'WAY',
    [string]$Mode   = 'invprobe'
)

$mapTaskName = 'ClaudeMapYDriveInvReport'
Unregister-ScheduledTask -TaskName $mapTaskName -Confirm:$false -ErrorAction SilentlyContinue
$mapAction    = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument '/c net use Y: \\Mac\Home /persistent:yes'
$mapTrigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$mapPrincipal = New-ScheduledTaskPrincipal -UserId 'joshuadavis' -LogonType Interactive -RunLevel Limited
$mapSettings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $mapTaskName -Action $mapAction -Trigger $mapTrigger -Principal $mapPrincipal -Settings $mapSettings -Force | Out-Null
Start-ScheduledTask -TaskName $mapTaskName
Start-Sleep -Seconds 4
Unregister-ScheduledTask -TaskName $mapTaskName -Confirm:$false -ErrorAction SilentlyContinue

$taskName = 'ClaudeInvReportBuild'
$ahk      = 'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe'
$arg      = '/ErrorStdOut "Y:\Documents\Claude\Projects\Bravo Data Extraction\InvReportBuild.ahk" ' + $Stores + ' ' + $Mode
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
$action    = New-ScheduledTaskAction -Execute $ahk -Argument $arg
$trigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$principal = New-ScheduledTaskPrincipal -UserId 'joshuadavis' -LogonType Interactive -RunLevel Limited
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 45)
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
Start-Sleep -Seconds 8
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
Write-Host ('invreport launched stores=' + $Stores)
