$ErrorActionPreference='Continue'
$u='joshuadavis'
$ahk='C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe'
$arg='"Y:\Documents\Claude\Projects\Bravo Data Extraction\_recover_to_dashboard.ahk" HAR'
Unregister-ScheduledTask -TaskName ClaudeRecover -Confirm:$false -ErrorAction SilentlyContinue
$a=New-ScheduledTaskAction -Execute $ahk -Argument $arg
$t=New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$pr=New-ScheduledTaskPrincipal -UserId $u -LogonType Interactive -RunLevel Limited
$s=New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName ClaudeRecover -Action $a -Trigger $t -Principal $pr -Settings $s -Force | Out-Null
Start-ScheduledTask -TaskName ClaudeRecover
Start-Sleep 8
Unregister-ScheduledTask -TaskName ClaudeRecover -Confirm:$false -ErrorAction SilentlyContinue
'recover-launch-done'
