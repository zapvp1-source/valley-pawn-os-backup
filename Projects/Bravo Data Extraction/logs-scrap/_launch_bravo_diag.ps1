$exe = Get-ChildItem "C:\Users\joshuadavis\AppData\Local\Apps\2.0" -Recurse -Filter 'Bravo.exe' -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
$taskName = 'ClaudeBravoLaunchDiag'
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
$a = New-ScheduledTaskAction -Execute $exe.FullName -WorkingDirectory $exe.DirectoryName
$p = New-ScheduledTaskPrincipal -UserId 'joshuadavis' -LogonType Interactive
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $taskName -Action $a -Principal $p -Settings $s -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
Start-Sleep -Seconds 12
schtasks /query /tn $taskName /fo LIST /v 2>&1 | Select-String "Last Result|Status"
Write-Output ("bravo count: " + (Get-Process | Where-Object { $_.ProcessName -match 'ravo' } | Measure-Object).Count)
