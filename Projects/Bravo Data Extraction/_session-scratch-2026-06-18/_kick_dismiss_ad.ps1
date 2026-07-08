# _kick_dismiss_ad.ps1 — runs _dismiss_ad.ahk in joshuadavis's interactive
# session (session 1) via a one-shot scheduled task, mirroring the technique
# in _restart_watcher.ps1. Needed because prlctl exec lands in session 0 and
# cannot interact with the Bravo GUI in session 1.
$taskName = "ClaudeDismissAdOnce"
$ahk      = "C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe"
$script   = '"Y:\Documents\Claude\Projects\Bravo Data Extraction\_dismiss_ad.ahk"'
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
$action    = New-ScheduledTaskAction -Execute $ahk -Argument $script
$trigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$principal = New-ScheduledTaskPrincipal -UserId "joshuadavis" -LogonType Interactive -RunLevel Limited
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
Start-Sleep -Seconds 10
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
Write-Host "dismiss-ad kick issued"
