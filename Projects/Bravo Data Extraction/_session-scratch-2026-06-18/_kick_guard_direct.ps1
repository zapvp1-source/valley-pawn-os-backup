# Run bravo_state_guard.ahk directly in Session 1 via a one-shot task,
# bypassing the watchdog, to isolate guard behavior. Also clears any stuck
# BravoStateGuard "Running" state.
$root = 'Y:\Documents\Claude\Projects\Bravo Data Extraction'
if (-not (Test-Path $root)) { $root = '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction' }
# reset the watchdog task if it is stuck Running
try { Stop-ScheduledTask -TaskName BravoStateGuard -ErrorAction SilentlyContinue } catch {}

$taskName = 'ClaudeGuardOnce'
$ahk      = 'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe'
$arg      = '"Y:\Documents\Claude\Projects\Bravo Data Extraction\bravo_state_guard.ahk"'
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
$action    = New-ScheduledTaskAction -Execute $ahk -Argument $arg
$trigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$principal = New-ScheduledTaskPrincipal -UserId 'joshuadavis' -LogonType Interactive -RunLevel Limited
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
Write-Host "guard kicked directly"
