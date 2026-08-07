schtasks /change /tn ScrapCloseoutWatcherWatchdog /enable | Out-Null
schtasks /run /tn ScrapCloseoutWatcherWatchdog | Out-Null
Start-Sleep -Seconds 10
schtasks /change /tn ScrapCloseoutWatcherWatchdog /disable | Out-Null
Get-WmiObject Win32_Process -Filter "Name='AutoHotkey64.exe'" | Select-Object ProcessId, CommandLine | Format-List
