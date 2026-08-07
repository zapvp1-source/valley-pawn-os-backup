Get-Process -Name AutoHotkey64 -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1
$p = Get-Process -Name AutoHotkey64 -ErrorAction SilentlyContinue
if ($p) { Write-Output "STILL_RUNNING" } else { Write-Output "ALL_KILLED" }
