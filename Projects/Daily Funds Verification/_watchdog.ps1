# _watchdog.ps1 — self-healing monitor for bravo_watcher.ahk
# Registered in Windows Task Scheduler as "BravoWatcherWatchdog", runs every 15 min.
# Restarts the watcher when it is dead, or hung (pending trigger + no activity 15+ min).
# Created 2026-06-11 after the 2026-06-10 15:29 hang stalled the trigger queue overnight.

$root = 'Y:\Documents\Claude\Projects\Bravo Data Extraction'
if (-not (Test-Path $root)) { $root = '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction' }
$log   = Join-Path $root 'logs\watchdog.log'
$stamp = Join-Path $root 'logs\watchdog.last_restart.txt'

function Log($m) { ("{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m) | Add-Content $log }

# --- 1. Is the watcher process alive? -----------------------------------
$alive = $false
Get-Process AutoHotkey64 -ErrorAction SilentlyContinue | ForEach-Object {
    $cmd = (Get-WmiObject Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine
    if ($cmd -like '*bravo_watcher.ahk*') { $alive = $true }
}

# --- 2. Hung check: pending trigger + no log/result activity 15+ min ----
# A busy watcher writes log lines constantly (pacing, cells, results), so
# "trigger waiting + nothing written for 15 min" reliably means hung —
# it does NOT false-positive during long multi-cell runs.
$pending = @(Get-ChildItem (Join-Path $root 'triggers') -Filter '*.json' -File -ErrorAction SilentlyContinue)
$lastAct = Get-ChildItem (Join-Path $root 'logs'), (Join-Path $root 'results') -File -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
$staleMin = if ($lastAct) { ((Get-Date) - $lastAct.LastWriteTime).TotalMinutes } else { 999 }
$hung = ($pending.Count -gt 0 -and $staleMin -gt 15)

if ($alive -and -not $hung) { exit 0 }   # healthy — stay quiet

# --- 3. Throttle: at most one restart per 20 min ------------------------
if (Test-Path $stamp) {
    if (((Get-Date) - (Get-Item $stamp).LastWriteTime).TotalMinutes -lt 20) {
        Log ("unhealthy (alive=$alive hung=$hung staleMin=" + [math]::Round($staleMin,1) + ") but throttled")
        exit 0
    }
}

# --- 4. Restart ----------------------------------------------------------
Log ("RESTART: alive=$alive pending=" + $pending.Count + " staleMin=" + [math]::Round($staleMin,1))
Get-Date -Format 'yyyy-MM-dd HH:mm:ss' | Set-Content $stamp
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root '_restart_watcher.ps1') *>> $log
Log "restart script finished"
