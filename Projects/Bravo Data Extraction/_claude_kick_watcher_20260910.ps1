$ErrorActionPreference = 'Continue'
$user = "joshuadavis"
$root = "\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction"
$taskName = "ClaudeWatcherKick0910"
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
$ahk = "C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe"
$watcher = '"' + $root + '\bravo_watcher.ahk"'
$action    = New-ScheduledTaskAction -Execute $ahk -Argument $watcher
$trigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddSeconds(5))
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
Start-Sleep -Seconds 15
Get-Process -Name AutoHotkey64 -ErrorAction SilentlyContinue | ForEach-Object {
  $cmd = (Get-CimInstance Win32_Process -Filter ("ProcessId=" + $_.Id)).CommandLine
  Write-Host ("AHK PID=" + $_.Id + " CMD=" + $cmd)
}
Start-Sleep -Seconds 5
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
Write-Host "=== KICK DONE ==="
