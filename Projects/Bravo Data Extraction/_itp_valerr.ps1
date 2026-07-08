# _itp_valerr.ps1 — kill stray /validate procs, then validate bravo_watcher.ahk
# with /ErrorStdOut so any syntax error is captured to a file instead of a
# blocking dialog. Writes exit code + stderr to _itp_valerr.txt.
$ErrorActionPreference = "Continue"
$base = "Y:\Documents\Claude\Projects\Bravo Data Extraction"
$ahk  = "C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe"
$out  = "$base\_itp_valerr.txt"
$err  = "$base\_itp_valerr_stderr.txt"

# kill any stray AutoHotkey /validate processes (NOT the running watcher)
Get-Process AutoHotkey64 -ErrorAction SilentlyContinue | ForEach-Object {
    $cl = (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine
    if ($cl -like "*/validate*") { try { Stop-Process -Id $_.Id -Force } catch {} }
}
Start-Sleep -Seconds 1

$watcher = Join-Path $base "bravo_watcher.ahk"
$p = Start-Process -FilePath $ahk -ArgumentList @("/ErrorStdOut", "/validate", ('"' + $watcher + '"')) -Wait -PassThru -WindowStyle Hidden -RedirectStandardError $err
Set-Content -Path $out -Value ("exit=" + $p.ExitCode) -Encoding utf8
if (Test-Path $err) {
    Add-Content -Path $out -Value "--- stderr ---" -Encoding utf8
    Get-Content $err | Add-Content -Path $out -Encoding utf8
}
