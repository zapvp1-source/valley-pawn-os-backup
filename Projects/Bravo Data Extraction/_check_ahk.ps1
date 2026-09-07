$p = Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'AutoHotkey64.exe' -and $_.CommandLine -like '*bravo_watcher*' }
if ($p) { $p | Select-Object Name,ProcessId,CommandLine | ConvertTo-Json } else { Write-Output 'NOT_RUNNING' }
