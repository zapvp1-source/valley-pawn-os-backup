$ErrorActionPreference='Continue'
$u='joshuadavis'
$ahk='C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe'
$arg='"Y:\Documents\Claude\Projects\Bravo Data Extraction\_nudge_login.ahk"'
Unregister-ScheduledTask -TaskName ClaudeNudge -Confirm:$false -ErrorAction SilentlyContinue
$a=New-ScheduledTaskAction -Execute $ahk -Argument $arg
$t=New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$p=New-ScheduledTaskPrincipal -UserId $u -LogonType Interactive -RunLevel Limited
$s=New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName ClaudeNudge -Action $a -Trigger $t -Principal $p -Settings $s -Force | Out-Null
Start-ScheduledTask -TaskName ClaudeNudge
Start-Sleep 10
Unregister-ScheduledTask -TaskName ClaudeNudge -Confirm:$false -ErrorAction SilentlyContinue
'nudge-session1-done'
