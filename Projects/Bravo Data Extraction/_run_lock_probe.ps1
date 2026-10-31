# _run_whatsnew.ps1 -- launch _lock_probe.ahk (cloned from _run_bravomapper.ps1, 2026-10-30) in joshuadavis Session 1 (additive, 2026-09-30).
# Same proven scheduled-task technique as _run_inspect.ps1 / _restart_watcher.ps1:
# map Y: in the interactive session first, then start AHK from Y:\ (never UNC).
# /ErrorStdOut keeps any AHK load error OFF the screen (no modal over Bravo).

$mapTaskName = 'ClaudeMapYDriveLockProbe'
Unregister-ScheduledTask -TaskName $mapTaskName -Confirm:$false -ErrorAction SilentlyContinue
$mapAction    = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument '/c net use Y: \\Mac\Home /persistent:yes'
$mapTrigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$mapPrincipal = New-ScheduledTaskPrincipal -UserId 'joshuadavis' -LogonType Interactive -RunLevel Limited
$mapSettings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $mapTaskName -Action $mapAction -Trigger $mapTrigger -Principal $mapPrincipal -Settings $mapSettings -Force | Out-Null
Start-ScheduledTask -TaskName $mapTaskName
Start-Sleep -Seconds 4
Unregister-ScheduledTask -TaskName $mapTaskName -Confirm:$false -ErrorAction SilentlyContinue

# 2026-10-30 v2: a v1 probe instance hung on a UIA Click(); stop ONLY processes running _lock_probe.ahk (never the watcher).
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*_lock_probe.ahk*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 2

$taskName = 'ClaudeLockProbe'
$ahk      = 'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe'
$arg      = '/ErrorStdOut "Y:\Documents\Claude\Projects\Bravo Data Extraction\_lock_probe.ahk"'
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
$cmdArg   = '/c ""' + $ahk + '" ' + $arg + ' > "Y:\Documents\Claude\Projects\Bravo Data Extraction\logs\_lock_probe_err2.txt" 2>&1"'
$action    = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument $cmdArg
$trigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$principal = New-ScheduledTaskPrincipal -UserId 'joshuadavis' -LogonType Interactive -RunLevel Limited
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
Start-Sleep -Seconds 30
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
Write-Host 'whatsnew launched'
