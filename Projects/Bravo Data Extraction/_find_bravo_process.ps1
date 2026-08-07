Get-Process | Where-Object { $_.ProcessName -like '*Bravo*' } | Select-Object Id,ProcessName,MainWindowTitle | Format-List
