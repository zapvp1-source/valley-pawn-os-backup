Get-Process | Where-Object { $_.MainWindowTitle -like "*Parallels*" } | Select-Object Id,ProcessName,MainWindowTitle
