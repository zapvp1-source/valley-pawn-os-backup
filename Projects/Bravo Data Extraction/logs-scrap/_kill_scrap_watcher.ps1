Stop-Process -Id 7900 -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Get-WmiObject Win32_Process -Filter "Name='AutoHotkey64.exe'" | Select-Object ProcessId, CommandLine | Format-List
