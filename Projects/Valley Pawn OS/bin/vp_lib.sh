#!/bin/bash
# vp_lib.sh — shared shell primitives for the native (launchd) Valley Pawn agents. Source it:
#   . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
# Everything here is the exact behaviour the Cowork SKILL.md files used to script through osascript.
# bash 3.2 compatible.

OS_DIR="$HOME/Documents/Claude/Projects/Valley Pawn OS"
BIN="$OS_DIR/bin"
BRAVO="$HOME/Documents/Claude/Projects/Bravo Data Extraction"
VLOG="$HOME/Library/Logs/valleypawn"; mkdir -p "$VLOG"
LEDGER="$OS_DIR/fleet/FAILURE_LEDGER.md"
VM='{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}'
PRLCTL=/usr/local/bin/prlctl
PY=/usr/bin/python3
slack() { "$PY" "$BIN/vp_slack.py" "$@"; }   # (a $SLACK string breaks on the space in "Valley Pawn OS")
export VP_TASK="${AGENT:-native}"           # every send through slack() leaves a receipt (vp_receipt.py)

vlog() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a "$VLOG/${AGENT:-native}.log"; }

# Failure policy v3: ONE ledger row, no DM. $1 task  $2 plain sentence  $3 needs-human text ("no" or "yes, ...")
ledger() {
  printf '| %s | %s | %s | NEEDS_HUMAN: %s | OPEN |\n' "$(date '+%Y-%m-%d %H:%M ET') (native)" "$1" "$2" "${3:-no}" >> "$LEDGER"
  vlog "LEDGER: $1 — $2"
}

# Single-instance lock per agent (stale after $2 minutes, default 90)
vp_lock() {
  local d="$VLOG/.lock.$1" stale="${2:-90}"
  if [ -d "$d" ] && [ -n "$(find "$VLOG" -maxdepth 1 -name ".lock.$1" -mmin +"$stale")" ]; then rmdir "$d"; fi
  mkdir "$d" 2>/dev/null || { vlog "another $1 is running — exit"; exit 0; }
  trap 'rmdir "'"$d"'" 2>/dev/null' EXIT
}

# Store calendar: stores open on a given date (YYYY-MM-DD). Sunday: none. Wednesday: CUL only.
open_stores() {
  local dow; dow=$(date -j -f %Y-%m-%d "$1" +%u)   # 1=Mon .. 7=Sun
  case "$dow" in 7) echo "" ;; 3) echo "CUL" ;; *) echo "CUL HAR LEX ROA WAY" ;; esac
}

# Bravo pipeline busy? (claimed trigger or result written in the last N minutes, default 6)
bravo_busy() { [ -n "$(find "$BRAVO/triggers/claimed" -type f -mmin -"${1:-6}" 2>/dev/null | head -1)$(find "$BRAVO/results" -name '*.result.json' -mmin -"${1:-6}" 2>/dev/null | head -1)" ]; }

# Health gate: run bravo_ensure_healthy.sh detached, wait for PASS/FAIL (cap seconds, default 600). Echoes status.
health_gate() {
  local cap="${1:-600}" t0=$(date +%s) s=""
  rm -f "$BRAVO/logs/_health_gate_status.txt"
  bravo_close_terminals >/dev/null 2>&1   # a console window over Bravo = "no-dashboard"; clear it before gating
  # LC_ALL=C: bravo_health_gate.sh strips the UTF-8 BOM from _recover_result.txt with `tr -d '\357\273\277'`,
  # which is byte-wise only in the C locale; under a UTF-8 locale the BOM survives, "^OK" never matches,
  # and a SUCCESSFUL recover is reported as "FAIL no-dashboard" (root-caused 2026-09-17 16:2x).
  ( cd "$BRAVO" && LC_ALL=C LANG=C nohup ./bravo_ensure_healthy.sh > logs/_hg_native.log 2>&1 < /dev/null & )
  while [ $(( $(date +%s) - t0 )) -lt "$cap" ]; do
    sleep 15; s=$(cat "$BRAVO/logs/_health_gate_status.txt" 2>/dev/null)
    case "$s" in *PASS*|*FAIL*) break ;; esac
  done
  echo "${s:-TIMEOUT}"
}

# Restart the VM watcher (singleton hygiene) — the exact call the SKILLs made.
# ALWAYS -WindowStyle Hidden: on this VM `prlctl exec powershell` opens a visible Windows Terminal
# window ON TOP of Bravo, and the UIA automation then reports "no-dashboard" (seen 2026-09-17 16:16).
vm_ps_file() { "$PRLCTL" exec "$VM" --current-user powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "$1"; }
# Non-UI commands run WITHOUT --current-user (Session 0): no console window can appear over Bravo at all.
vm_ps_cmd()  { "$PRLCTL" exec "$VM" powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -Command "$1"; }
watcher_restart() { vm_ps_file '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\_restart_watcher_v2.ps1' > /tmp/vp_watcher_restart.log 2>&1; }
bravo_relaunch()  { vm_ps_file 'Y:\Documents\Claude\Projects\Bravo Data Extraction\_relaunch_bravo_and_watcher.ps1' > /tmp/vp_bravo_relaunch.log 2>&1; }
bravo_procs() {  # prints Bravo.exe / dfsvc.exe names if running
  vm_ps_cmd "Get-CimInstance Win32_Process | Where-Object { \$_.Name -eq 'Bravo.exe' -or \$_.Name -eq 'dfsvc.exe' } | Select-Object -ExpandProperty Name" 2>/dev/null
}
# Close stray console windows (Windows Terminal / conhost-hosted powershell) that cover Bravo. Never touches Bravo, AHK, or the watcher.
bravo_close_terminals() {
  vm_ps_cmd "Get-Process WindowsTerminal,OpenConsole -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue; Get-Process powershell -ErrorAction SilentlyContinue | Where-Object { \$_.MainWindowHandle -ne 0 -and \$_.Id -ne \$PID } | Stop-Process -Force -ErrorAction SilentlyContinue; 'closed'" 2>/dev/null | tail -1
}

# Drop a trigger and wait for its result. $1 id  $2 reports-json-array-body  $3 cap seconds (default 3000)
# One self-heal (watcher restart) if unclaimed >3 min or log silent >12 min. Returns 0 when result exists.
bravo_run() {
  local id="$1" reports="$2" cap="${3:-3000}"
  printf '{"id":"%s","requested_at":"%s","reports":[%s]}' "$id" "$(date +%Y-%m-%dT%H:%M:%S%z)" "$reports" > "$BRAVO/triggers/$id.json"
  vlog "trigger written: $id"
  local t0=$(date +%s) healed=0 last_size=0 last_change=$(date +%s) now size unclaimed
  while [ $(( $(date +%s) - t0 )) -lt "$cap" ]; do
    [ -f "$BRAVO/results/$id.result.json" ] && { vlog "result ready: $id"; return 0; }
    sleep 20; now=$(date +%s)
    size=$(stat -f %z "$BRAVO/logs/$id.log" 2>/dev/null || echo 0)
    [ "$size" != "$last_size" ] && { last_size=$size; last_change=$now; }
    unclaimed=0; [ -f "$BRAVO/triggers/$id.json" ] && unclaimed=1
    if [ $healed -eq 0 ] && { { [ $unclaimed -eq 1 ] && [ $((now - t0)) -gt 180 ]; } || { [ $unclaimed -eq 0 ] && [ $((now - last_change)) -gt 720 ]; }; }; then
      vlog "self-heal for $id: unclaimed=$unclaimed silent=$((now - last_change))s"
      if bravo_procs | grep -q Bravo.exe; then watcher_restart; else bravo_relaunch; fi
      healed=1; sleep 120
    fi
  done
  vlog "TIMEOUT waiting for $id"; return 1
}

# JSON array body of stores: "CUL HAR" -> "CUL","HAR"
stores_json() { echo "$1" | tr ' ' '\n' | sed 's/.*/"&"/' | paste -sd, -; }
