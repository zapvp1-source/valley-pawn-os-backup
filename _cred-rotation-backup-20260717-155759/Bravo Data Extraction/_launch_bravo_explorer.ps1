# _launch_bravo_explorer.ps1 — launch Bravo via explorer.exe (Session 1)
$name = 'ClaudeBravoLaunchExp'
$bravoShortcut = 'C:\Users\joshuadavis\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Bravo Store Systems\Bravo.appref-ms'
Unregister-ScheduledTask -TaskName $name -Confirm:$false -ErrorAction SilentlyContinue
$action    = New-ScheduledTaskAction -Execute 'explorer.exe' -Argument ('"' + $bravoShortcut + '"')
$trigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$principal = New-ScheduledTaskPrincipal -UserId 'joshuadavis' -LogonType Interactive -RunLevel Limited
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $name
Start-Sleep -Seconds 18
Get-Process -Name 'Bravo*','dfsvc' -ErrorAction SilentlyContinue | ForEach-Object { Write-Host ("PROC " + $_.ProcessName + " PID=" + $_.Id) }
Start-Sleep -Seconds 15
Get-Process -Name 'Bravo*','dfsvc' -ErrorAction SilentlyContinue | ForEach-Object { Write-Host ("PROC2 " + $_.ProcessName + " PID=" + $_.Id) }
Unregister-ScheduledTask -TaskName $name -Confirm:$false -ErrorAction SilentlyContinue
Write-Host 'done'
