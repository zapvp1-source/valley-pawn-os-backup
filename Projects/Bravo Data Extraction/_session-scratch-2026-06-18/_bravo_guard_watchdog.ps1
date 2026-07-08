# _bravo_guard_watchdog.ps1 — runs bravo_state_guard.ahk to keep BRAVO's UI
# healthy (logged-in Dashboard), complementing _watchdog.ps1 which only keeps
# the WATCHER PROCESS alive. Registered as scheduled task "BravoStateGuard"
# (interactive Session 1) every 10 min.
#
# SAFETY: only heals Bravo when the watcher is IDLE. A running report writes
# log/result lines far more often than every few minutes (pacing cooldowns are
# 15s), so "no log/result activity for >4 min" reliably means no active run —
# the guard then never collides with a live report driving Bravo.
$root = 'Y:\Documents\Claude\Projects\Bravo Data Extraction'
if (-not (Test-Path $root)) { $root = '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction' }
$log = Join-Path $root 'logs\bravo_guard_watchdog.log'
function Log($m) { ("{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m) | Add-Content $log }

# 1. Skip if a guard run is already in progress
$already = Get-Process AutoHotkey64 -ErrorAction SilentlyContinue | Where-Object {
    (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine -like '*bravo_state_guard.ahk*'
}
if ($already) { exit 0 }

# 2. Skip if the watcher is mid-run (fresh PER-RUN log/result activity).
#    Exclude heartbeat/maintenance files that tick constantly and would
#    otherwise mask idleness: foreground_keeper.log, watchdog logs, the
#    watcher start stamp, and this guard's own logs/markers.
$exclude = @('foreground_keeper.log','watchdog.log','watchdog.last_restart.txt',
             'watcher.last_started.txt','bravo_guard_watchdog.log',
             'bravo_guard_result.txt','bravo_health_alert.txt')
$lastAct = Get-ChildItem (Join-Path $root 'logs'), (Join-Path $root 'results') -File -ErrorAction SilentlyContinue |
    Where-Object { $exclude -notcontains $_.Name -and $_.Name -notlike 'bravo_guard_*' -and $_.Name -notlike 'bravo_selfheal*' } |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
$staleMin = if ($lastAct) { ((Get-Date) - $lastAct.LastWriteTime).TotalMinutes } else { 999 }
if ($staleMin -lt 4) { exit 0 }   # watcher busy — do not touch Bravo

# 3. Run the guard (synchronous; it writes logs\bravo_guard_result.txt)
$ahk    = 'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe'
$script = Join-Path $root 'bravo_state_guard.ahk'
Log ("running guard (staleMin=" + [math]::Round($staleMin,1) + ")")
Start-Process -FilePath $ahk -ArgumentList ('"' + $script + '"') -Wait

# 4. Read result; on unrecoverable, drop an alert marker the Mac side reads
$resultFile = Join-Path $root 'logs\bravo_guard_result.txt'
$result = if (Test-Path $resultFile) { (Get-Content $resultFile -Raw).Trim() } else { 'NO_RESULT' }
Log ("guard result: " + $result)
$alertFile = Join-Path $root 'logs\bravo_health_alert.txt'
if ($result -like 'FAIL*' -or $result -eq 'NO_RESULT') {
    ("{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $result) | Set-Content $alertFile
    Log "ALERT marker written (human attention needed)"
} else {
    if (Test-Path $alertFile) { Remove-Item $alertFile -Force -ErrorAction SilentlyContinue }
}
exit 0
