Write-Output "=== AHK running ==="
Get-WmiObject Win32_Process -Filter "Name='AutoHotkey64.exe'" | Select-Object ProcessId, CommandLine | Format-List | Out-String
Write-Output "=== keeper log tail ==="
$p = 'Y:\Documents\Claude\Projects\Bravo Data Extraction\logs\foreground_keeper.log'
if (Test-Path $p) { Get-Content $p -Tail 15 | Out-String } else { Write-Output "no keeper log at $p" }
Write-Output "=== any *keeper* logs ==="
Get-ChildItem 'Y:\Documents\Claude\Projects\Bravo Data Extraction\logs' -Filter '*keeper*' -ErrorAction SilentlyContinue |
  Select-Object Name, LastWriteTime | Format-Table -AutoSize | Out-String
