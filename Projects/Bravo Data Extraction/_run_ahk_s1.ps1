# _run_ahk_s1.ps1 — run an AHK script in Session 1 via the scheduled-task trick.
# Usage: powershell -File _run_ahk_s1.ps1 <scriptName.ahk>
param([string]$ScriptName = '_bravo_probe.ahk')
$name = 'ClaudeAhkS1'
$ahk  = 'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe'
$scriptPath = 'Y:\Documents\Claude\Projects\Bravo Data Extraction\' + $ScriptName
Unregister-ScheduledTask -TaskName $name -Confirm:$false -ErrorAction SilentlyContinue
$action    = New-ScheduledTaskAction -Execute $ahk -Argument ('"' + $scriptPath + '"')
$trigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$principal = New-ScheduledTaskPrincipal -UserId 'joshuadavis' -LogonType Interactive -RunLevel Limited
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $name
Start-Sleep -Seconds 10
Unregister-ScheduledTask -TaskName $name -Confirm:$false -ErrorAction SilentlyContinue
Write-Host ('ahk-spawned: ' + $ScriptName)
