$root = 'Y:\Documents\Claude\Projects\Bravo Data Extraction'
if (-not (Test-Path $root)) { $root = '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction' }
$ahk = 'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe'
$guard = Join-Path $root 'bravo_state_guard.ahk'
$tmp = Join-Path $env:TEMP ('guard_validate_' + (Get-Random) + '.txt')
& $ahk '/ErrorStdOut' '/validate' $guard *> $tmp
Write-Host "=== validate output (empty = syntax OK) ==="
if (Test-Path $tmp) { Get-Content $tmp } else { Write-Host '(no output)' }
Remove-Item $tmp -ErrorAction SilentlyContinue
