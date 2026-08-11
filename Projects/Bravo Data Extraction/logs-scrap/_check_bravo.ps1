Get-Process | Where-Object { $_.MainWindowTitle -ne "" } | Select-Object Id, ProcessName, MainWindowTitle | Format-List
Write-Output "=== bravo-ish processes ==="
Get-Process | Where-Object { $_.ProcessName -like "*ravo*" -or $_.ProcessName -like "*ZTI*" } | Select-Object Id, ProcessName, MainWindowTitle | Format-List
