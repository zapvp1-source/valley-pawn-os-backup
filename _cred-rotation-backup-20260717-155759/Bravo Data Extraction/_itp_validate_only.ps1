# _itp_validate_only.ps1 — validate the two dispatch files (no restart).
$ErrorActionPreference = "Continue"
$base = "Y:\Documents\Claude\Projects\Bravo Data Extraction"
$ahk  = "C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe"
$st   = "$base\_itp_validate_only.txt"
Set-Content -Path $st -Value ("VSTART " + (Get-Date -Format o)) -Encoding utf8
foreach ($s in @("bravo_watcher.ahk","bravo_export.ahk")) {
    $script = Join-Path $base $s
    $p = Start-Process -FilePath $ahk -ArgumentList @("/validate", ('"' + $script + '"')) -Wait -PassThru -WindowStyle Hidden
    Add-Content -Path $st -Value ("VAL " + $s + " exit=" + $p.ExitCode) -Encoding utf8
}
Add-Content -Path $st -Value ("VDONE " + (Get-Date -Format o)) -Encoding utf8
