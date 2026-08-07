# _run_scrap_watcher_macpath.ps1 - one-off launcher, explicit Mac-shared path
# (avoids the Y: mapped-drive assumption in _run_ahk_s1.ps1, which may not
# resolve inside a freshly-spawned scheduled-task logon session)
$name = 'ClaudeScrapS1'
$ahk  = 'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe'
$scriptPath = 'C:\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\ScrapBucketCloseoutWatcher.ahk'
Unregister-ScheduledTask -TaskName $name -Confirm:$false -ErrorAction SilentlyContinue
$action    = New-ScheduledTaskAction -Execute $ahk -Argument ('"' + $scriptPath + '"')
$trigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddSeconds(5))
$principal = New-ScheduledTaskPrincipal -UserId 'joshuadavis' -LogonType Interactive -RunLevel Limited
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Start-Sleep -Seconds 10
Unregister-ScheduledTask -TaskName $name -Confirm:$false -ErrorAction SilentlyContinue
Write-Host ('relaunched: ' + $scriptPath)
