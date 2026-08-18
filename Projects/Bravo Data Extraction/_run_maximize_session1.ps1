$ErrorActionPreference='Continue'
$u='joshuadavis'
$ahk='C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe'
$arg='"Y:\Documents\Claude\Projects\Bravo Data Extraction\_maximize_bravo.ahk"'
Unregister-ScheduledTask -TaskName ClaudeMaximize -Confirm:$false -ErrorAction SilentlyContinue
$a=New-ScheduledTaskAction -Execute $ahk -Argument $arg
$t=New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$p=New-ScheduledTaskPrincipal -UserId $u -LogonType Interactive -RunLevel Limited
$s=New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName ClaudeMaximize -Action $a -Trigger $t -Principal $p -Settings $s -Force | Out-Null
Start-ScheduledTask -TaskName ClaudeMaximize
Start-Sleep 8
Unregister-ScheduledTask -TaskName ClaudeMaximize -Confirm:$false -ErrorAction SilentlyContinue
'maximize-session1-done'
