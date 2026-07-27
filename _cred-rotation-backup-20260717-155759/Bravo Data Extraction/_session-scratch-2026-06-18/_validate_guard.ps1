$root = 'Y:\Documents\Claude\Projects\Bravo Data Extraction'
if (-not (Test-Path $root)) { $root = '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction' }
$ahk = 'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe'

# 1. Kill any stuck guard process (holding an error dialog) + the watchdog waiting on it
Get-Process AutoHotkey64 -ErrorAction SilentlyContinue | ForEach-Object {
    $c = (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine
    if ($c -like '*bravo_state_guard.ahk*') { Write-Host ("kill guard PID=" + $_.Id); Stop-Process -Id $_.Id -Force }
}
Get-Process powershell -ErrorAction SilentlyContinue | ForEach-Object {
    $c = (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine
    if ($c -like '*_bravo_guard_watchdog.ps1*') { Write-Host ("kill watchdog PID=" + $_.Id); Stop-Process -Id $_.Id -Force }
}
Start-Sleep 1

# 2. Validate syntax (does NOT execute the script)
$guard = Join-Path $root 'bravo_state_guard.ahk'
$tmp = Join-Path $env:TEMP 'guard_validate.txt'
& $ahk '/ErrorStdOut' '/validate' $guard 2> $tmp 1> $tmp
Write-Host "=== validate output (empty = syntax OK) ==="
if (Test-Path $tmp) { Get-Content $tmp } else { Write-Host '(no output captured)' }
