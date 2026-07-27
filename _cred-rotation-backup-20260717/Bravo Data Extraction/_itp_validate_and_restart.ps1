# _itp_validate_and_restart.ps1
# Additive helper for the items-to-price cell rollout (2026-06-09).
#
# Validates bravo_watcher.ahk + bravo_export.ahk (which now #Include the new
# reports\ItemsToPrice.ahk) with AutoHotkey's /validate BEFORE restarting the
# watcher. If EITHER fails to validate, the currently-running watcher is left
# completely untouched — so no production pipeline task (daily funds, EOM,
# Monday combined run, etc.) is put at risk by a load-time syntax error.
# Only on a clean validation does it call the canonical _restart_watcher.ps1.
#
# Writes a human-readable status file the Mac side polls via osascript.
$ErrorActionPreference = "Continue"
$base   = "Y:\Documents\Claude\Projects\Bravo Data Extraction"
$ahk    = "C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe"
$status = "$base\_itp_restart_status.txt"

Set-Content -Path $status -Value ("START " + (Get-Date -Format o)) -Encoding utf8

$ok = $true
foreach ($s in @("bravo_watcher.ahk", "bravo_export.ahk")) {
    $script = Join-Path $base $s
    try {
        $p = Start-Process -FilePath $ahk -ArgumentList @("/validate", ('"' + $script + '"')) -Wait -PassThru -WindowStyle Hidden
        $code = $p.ExitCode
    } catch {
        $code = 999
        Add-Content -Path $status -Value ("VALIDATE " + $s + " EXCEPTION " + $_.Exception.Message) -Encoding utf8
    }
    Add-Content -Path $status -Value ("VALIDATE " + $s + " exit=" + $code) -Encoding utf8
    if ($code -ne 0) { $ok = $false }
}

if (-not $ok) {
    Add-Content -Path $status -Value "ABORT validation_failed watcher_NOT_restarted" -Encoding utf8
    exit 1
}

Add-Content -Path $status -Value "VALIDATION_OK restarting_watcher" -Encoding utf8
try {
    $log = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $base "_restart_watcher.ps1") 2>&1 | Out-String
    Add-Content -Path $status -Value $log -Encoding utf8
} catch {
    Add-Content -Path $status -Value ("RESTART_EXCEPTION " + $_.Exception.Message) -Encoding utf8
}
Add-Content -Path $status -Value ("RESTART_DONE " + (Get-Date -Format o)) -Encoding utf8
