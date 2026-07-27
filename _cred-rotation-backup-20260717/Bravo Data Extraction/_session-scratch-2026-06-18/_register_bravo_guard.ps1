# _register_bravo_guard.ps1 — ONE-TIME registration of the "BravoStateGuard"
# scheduled task. Runs _bravo_guard_watchdog.ps1 every 10 minutes in
# joshuadavis's interactive Session 1 (so the guard can drive the Bravo GUI).
# Additive — runs ALONGSIDE the existing "BravoWatcherWatchdog" (process heal);
# this one heals Bravo's UI state.
$name   = 'BravoStateGuard'
$script = '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\_bravo_guard_watchdog.ps1'
Unregister-ScheduledTask -TaskName $name -Confirm:$false -ErrorAction SilentlyContinue
$action    = New-ScheduledTaskAction -Execute 'powershell.exe' `
             -Argument ('-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "' + $script + '"')
$trigger   = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
             -RepetitionInterval (New-TimeSpan -Minutes 10) `
             -RepetitionDuration (New-TimeSpan -Days 3650)
$principal = New-ScheduledTaskPrincipal -UserId 'joshuadavis' -LogonType Interactive -RunLevel Limited
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger `
    -Principal $principal -Settings $settings -Force | Out-Null
Write-Host 'BravoStateGuard registered: every 10 minutes'
