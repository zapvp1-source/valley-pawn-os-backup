$p = Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'dfsvc.exe' }
if ($p) { $p | Select-Object Name,ProcessId | ConvertTo-Json } else { Write-Output 'NOT_RUNNING' }
