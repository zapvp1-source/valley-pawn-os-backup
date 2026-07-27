# _enum_session1.ps1 — run _enum_windows.ps1 in Session 1, output to logs\_enum_s1.txt
$name = 'ClaudeEnumS1'
$inner = '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\_enum_windows.ps1'
$out   = '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\logs\_enum_s1.txt'
Unregister-ScheduledTask -TaskName $name -Confirm:$false -ErrorAction SilentlyContinue
$arg = '-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -Command "& ''' + $inner + ''' | Out-File -FilePath ''' + $out + ''' -Encoding utf8"'
$action    = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $arg
$trigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$principal = New-ScheduledTaskPrincipal -UserId 'joshuadavis' -LogonType Interactive -RunLevel Limited
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $name
Start-Sleep -Seconds 8
Unregister-ScheduledTask -TaskName $name -Confirm:$false -ErrorAction SilentlyContinue
Write-Host 'enum-done'
