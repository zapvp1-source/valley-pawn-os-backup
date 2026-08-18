# _restart_watcher_v2.ps1 - shipped 2026-08-16 (additive hardening, sold-review incident)
# PREFERRED entry point for watcher restarts. Wraps _restart_watcher.ps1 (unmodified):
#   1. sweeps stale claimed triggers (_cleanup_stale_claims.ps1) so orphaned claims
#      from a crashed run cannot confuse post-restart triage
#   2. runs the original _restart_watcher.ps1
#   3. VERIFIES within 60s that a real watcher process (bravo_watcher.ahk cmdline)
#      is running, and whether logs\watcher.last_started.txt advanced.
#      Writes PASS/FAIL to logs\_restart_watcher_v2.log so callers can tell a
#      real restart from a silent failure (2026-08-02 / 2026-08-16 lesson).
# Run in-VM via prlctl exec ... powershell -NoProfile -ExecutionPolicy Bypass -File
#   "Y:\Documents\Claude\Projects\Bravo Data Extraction\_restart_watcher_v2.ps1"
$root = "Y:\Documents\Claude\Projects\Bravo Data Extraction"
$log  = Join-Path $root "logs\_restart_watcher_v2.log"
function VLog($m) { Add-Content -Path $log -Value ("{0} {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $m); Write-Host $m }
VLog "=== restart_watcher_v2 start ==="
try {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root "_cleanup_stale_claims.ps1") | ForEach-Object { VLog ("step1: " + $_) }
} catch { VLog ("step1: sweep error (continuing to restart): " + $_) }
$marker = Join-Path $root "logs\watcher.last_started.txt"
$beforeStamp = if (Test-Path $marker) { (Get-Item $marker).LastWriteTime } else { Get-Date "2000-01-01" }
VLog "step2: running original _restart_watcher.ps1"
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root "_restart_watcher.ps1") | ForEach-Object { VLog ("step2: " + $_) }
$ok = $false
$pid2 = 0
for ($i = 0; $i -lt 12; $i++) {
    Start-Sleep -Seconds 5
    $proc = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.Name -eq "AutoHotkey64.exe" -and $_.CommandLine -like "*bravo_watcher.ahk*" } | Select-Object -First 1
    if ($proc) { $ok = $true; $pid2 = $proc.ProcessId; break }
}
$stampAdvanced = (Test-Path $marker) -and ((Get-Item $marker).LastWriteTime -gt $beforeStamp)
if ($ok) {
    VLog ("step3: PASS - watcher PID=" + $pid2 + " running; start-marker advanced=" + $stampAdvanced)
    if (-not $stampAdvanced) { VLog "step3: WARN - watcher.last_started.txt did not advance (known stale-marker issue) - trust the live PID, but watch the next claim" }
} else {
    VLog "step3: FAIL - no bravo_watcher.ahk process within 60s. Escalate to _relaunch_bravo_and_watcher.ps1 (do NOT keep re-running this)."
}
$queue = (Get-ChildItem (Join-Path $root "triggers\claimed") -Filter *.json -File -ErrorAction SilentlyContinue | Measure-Object).Count
VLog ("claimed-queue depth after restart: " + $queue + " (watcher is SERIAL - a busy queue means new triggers wait, not that the watcher is dead)")
VLog "=== restart_watcher_v2 done ==="
