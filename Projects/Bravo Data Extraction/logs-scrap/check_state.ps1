Write-Output "--- Bravo process ---"
Get-Process -Name "*Bravo*" -ErrorAction SilentlyContinue | Select-Object Id,ProcessName,MainWindowTitle
Write-Output "--- BravoWatcherWatchdog task ---"
schtasks /query /tn BravoWatcherWatchdog /fo LIST | Select-String "TaskName|Status|Scheduled Task State|Last Run Time|Last Result"
Write-Output "--- ScrapCloseoutWatcherWatchdog task ---"
schtasks /query /tn ScrapCloseoutWatcherWatchdog /fo LIST | Select-String "TaskName|Status|Scheduled Task State"
Write-Output "--- Any AutoHotkey ---"
Get-Process -Name "AutoHotkey64" -ErrorAction SilentlyContinue
