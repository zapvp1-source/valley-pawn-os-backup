# _launch_bravo_only.ps1 — launch Bravo (ClickOnce) in Session 1, leave watcher alone.
# v2: verify shortcut, launch via rundll32 dfshim.dll (more reliable than start appref-ms)
$name = 'ClaudeBravoLaunchOnly'
$bravoShortcut = 'C:\Users\joshuadavis\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Bravo Store Systems\Bravo.appref-ms'

if (Test-Path $bravoShortcut) { Write-Host 'shortcut: EXISTS' } else {
    Write-Host 'shortcut: MISSING — searching...'
    Get-ChildItem 'C:\Users\joshuadavis\AppData\Roaming\Microsoft\Windows\Start Menu\Programs' -Recurse -Filter '*.appref-ms' -ErrorAction SilentlyContinue |
        ForEach-Object { Write-Host ('found: ' + $_.FullName) }
    exit 1
}

Unregister-ScheduledTask -TaskName $name -Confirm:$false -ErrorAction SilentlyContinue
$action    = New-ScheduledTaskAction -Execute 'rundll32.exe' -Argument ('dfshim.dll,ShOpenVerbShortcut "' + $bravoShortcut + '"')
$trigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$principal = New-ScheduledTaskPrincipal -UserId 'joshuadavis' -LogonType Interactive -RunLevel Limited
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $name
Start-Sleep -Seconds 20
$procs = Get-Process -Name 'Bravo*','dfsvc' -ErrorAction SilentlyContinue
if ($procs) { $procs | ForEach-Object { Write-Host ("PROC " + $_.ProcessName + " PID=" + $_.Id + " Session=" + $_.SessionId) } }
else { Write-Host 'WARN: no Bravo/dfsvc process visible after 20s' }
Unregister-ScheduledTask -TaskName $name -Confirm:$false -ErrorAction SilentlyContinue
