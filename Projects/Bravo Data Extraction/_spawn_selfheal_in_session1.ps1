
$ErrorActionPreference = 'Continue'
$user = 'joshuadavis'
$ahk = 'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe'
$script = '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\_selfheal.ahk'
$taskName = 'ClaudeBravoSelfHeal'
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
$action = New-ScheduledTaskAction -Execute $ahk -Argument ('"' + $script + '"')
$trigger = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
Write-Host ('STARTED ' + $taskName)

