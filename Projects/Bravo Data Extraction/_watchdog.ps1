# _watchdog.ps1 — self-healing monitor for bravo_watcher.ahk
# Registered in Windows Task Scheduler as "BravoWatcherWatchdog", runs every 2 min.
# Restarts the watcher when it is dead, or hung (pending trigger + no activity 4+ min).
# Created 2026-06-11 after the 2026-06-10 15:29 hang stalled the trigger queue overnight.
#
# TIGHTENED 2026-08-02 after a ROA store-switch double-click hung the watcher for
# 10+ min (no log output at all — the hang was inside a blocking UIA .Click() COM
# call) while this watchdog stayed silent. Root-caused to TWO compounding bugs,
# both fixed here:
#   (a) staleness was computed over EVERY file in logs\ + results\, which is
#       shared by every other scheduled automation (funds verification, KPIs,
#       etc.) — any unrelated task writing a log file reset the "activity" clock
#       and masked a truly-hung watcher. Now scoped to ONLY the pending
#       trigger's own <triggerId>.log / <triggerId>.result.json.
#   (b) the 15-min schedule interval + 15-min staleness threshold meant up to
#       ~30 min could pass before a hang was even detected. Tightened to a
#       2-min poll / 4-min staleness threshold (comfortably above the ~90s max
#       gap seen during normal grid-walk/session-switch waits), so worst-case
#       detection+restart latency drops from ~30-45 min to ~6 min.
# See BRAVO_KNOWN_ISSUES.md for the full incident history this addresses.

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

# --- 2. Hung check: pending trigger + no activity on THAT trigger's OWN --
# log/result file for 4+ min. Scoped per-trigger (by id) so unrelated
# automations writing elsewhere in logs\ can't mask a real hang.
$pending = @(Get-ChildItem (Join-Path $root 'triggers') -Filter '*.json' -File -ErrorAction SilentlyContinue)
$staleMin = 999
if ($pending.Count -gt 0) {
    $staleMins = foreach ($p in $pending) {
        $id = [IO.Path]::GetFileNameWithoutExtension($p.Name)
        $candidates = @(
            (Join-Path $root ("logs\" + $id + ".log")),
            (Join-Path $root ("results\" + $id + ".result.json"))
        ) | Where-Object { Test-Path $_ } | ForEach-Object { Get-Item $_ }
        if ($candidates.Count -gt 0) {
            $newest = $candidates | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            ((Get-Date) - $newest.LastWriteTime).TotalMinutes
        } else {
            # Trigger dropped but its own log hasn't been created yet — use the
            # trigger file's own age as the clock (covers a watcher that's dead
            # before it even claims the trigger).
            ((Get-Date) - $p.LastWriteTime).TotalMinutes
        }
    }
    $staleMin = ($staleMins | Measure-Object -Minimum).Minimum
}
$hung = ($pending.Count -gt 0 -and $staleMin -gt 4)

if ($alive -and -not $hung) { exit 0 }   # healthy — stay quiet

# --- 3. Throttle: at most one restart per 8 min --------------------------
if (Test-Path $stamp) {
    if (((Get-Date) - (Get-Item $stamp).LastWriteTime).TotalMinutes -lt 8) {
        Log ("unhealthy (alive=$alive hung=$hung staleMin=" + [math]::Round($staleMin,1) + ") but throttled")
        exit 0
    }
}

# --- 4. Restart ----------------------------------------------------------
Log ("RESTART: alive=$alive pending=" + $pending.Count + " staleMin=" + [math]::Round($staleMin,1))
Get-Date -Format 'yyyy-MM-dd HH:mm:ss' | Set-Content $stamp
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root '_restart_watcher.ps1') *>> $log
Log "restart script finished"
