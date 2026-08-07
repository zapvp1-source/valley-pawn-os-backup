Write-Output "--- BravoWatcherWatchdog ---"
schtasks /query /tn BravoWatcherWatchdog /fo LIST 2>&1
Write-Output "--- ScrapCloseoutWatcherWatchdog ---"
schtasks /query /tn ScrapCloseoutWatcherWatchdog /fo LIST 2>&1
