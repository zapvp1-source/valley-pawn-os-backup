$ahk = 'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe'
$script = 'Y:\Documents\Claude\Projects\Bravo Data Extraction\_nics_validate.ahk'
$out = 'Y:\Documents\Claude\Projects\Bravo Data Extraction\logs\_nics_validate_result.txt'
if (-not (Test-Path (Split-Path $out))) { $out = '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\logs\_nics_validate_result.txt' }
$stdout = & $ahk '/validate' $script 2>&1
$code = $LASTEXITCODE
"VALIDATE_EXIT=$code`r`n--- output ---`r`n$stdout" | Set-Content $out
Write-Host "validate done exit=$code"
