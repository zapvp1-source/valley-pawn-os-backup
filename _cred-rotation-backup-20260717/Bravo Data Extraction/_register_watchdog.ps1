# _register_watchdog.ps1 — ONE-TIME registration of the BravoWatcherWatchdog
# Windows Task Scheduler job. Run once as joshuadavis; after this the VM
# heals its own watcher and no external restarts are ever needed.

$name   = 'BravoWatcherWatchdog'
$script = '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\_watchdog.ps1'

Unregister-ScheduledTask -TaskName $name -Confirm:$false -ErrorAction SilentlyContinue

$action    = New-ScheduledTaskAction -Execute 'powershell.exe' `
             -Argument ('-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "' + $script + '"')
$trigger   = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
             -RepetitionInterval (New-TimeSpan -Minutes 15) `
             -RepetitionDuration (New-TimeSpan -Days 3650)
$principal = New-ScheduledTaskPrincipal -UserId 'joshuadavis' -LogonType Interactive -RunLevel Limited
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger `
    -Principal $principal -Settings $settings -Force | Out-Null
Write-Host 'Watchdog registered: every 15 minutes'

# Kick it immediately so the currently-hung watcher gets restarted right now
Start-ScheduledTask -TaskName $name
Write-Host 'Watchdog started now'
