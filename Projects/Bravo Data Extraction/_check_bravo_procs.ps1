Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'Bravo.exe' -or $_.Name -eq 'dfsvc.exe' } | Select-Object Name,ProcessId | ConvertTo-Json
