# Run _setres.ps1 in joshuadavis Session 1 (interactive) so the display change
# applies to the console session where Bravo runs.
$taskName = 'ClaudeSetRes'
$ps       = 'powershell.exe'
$arg      = '-NoProfile -ExecutionPolicy Bypass -File "\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\_setres.ps1"'
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
$action    = New-ScheduledTaskAction -Execute $ps -Argument $arg
$trigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$principal = New-ScheduledTaskPrincipal -UserId 'joshuadavis' -LogonType Interactive -RunLevel Limited
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
Start-Sleep 6
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
Write-Host "setres kicked in session 1"
