$ahk = 'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe'
$base = '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction'
$script = "$base\bravo_watcher.ahk"
$out = "$base\logs\_nics_watcher_validate.txt"
$err = & $ahk '/ErrorStdOut' '/validate' $script 2>&1 | Out-String
$code = $LASTEXITCODE
"EXIT=$code`r`n--- errors (blank = clean) ---`r`n$err" | Set-Content -Path $out
Write-Host "done exit=$code"
