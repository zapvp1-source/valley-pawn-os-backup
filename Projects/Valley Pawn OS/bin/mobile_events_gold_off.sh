#!/bin/bash
# mobile_events_gold_off.sh [STORES] [off|channels] (2026-11-19, Joshua: gold app message off at all stores). Launches Bravo Data Extraction/MobileEventsRead.ahk,
# which opens Customers > Schedule Mobile Event per store, writes what it shows to output/mobile_events/, and
# leaves by the editor's Cancel. Clone of bravo_map_run.sh's guard/monitor/recovery. Silent (Rule 16).
AGENT=mobile-events-goldoff; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; vp_lock $AGENT 60
STORES="${1:-WAY}"; MODE="${2:-off}"
OUT="$BRAVO/output/mobile_events"; ST="$OUT/_status.txt"; mkdir -p "$OUT"
G="$BRAVO/_bravo_foreground_guard.sh"
busy_reason() {
  pgrep -f "monthly_prestage_runner.py" >/dev/null && { echo "month-end prestage running"; return; }
  pgrep -f "bravo_pull.sh|monday_pull.sh|morning_pull.sh|daily_report.sh|scrap_closeout_run.sh|forfeiture_winback_weekly.sh|bravo_relaunch.sh|bravo_ensure_healthy|funds_verification.sh|bravo_map_run.sh" >/dev/null && { echo "a Bravo job is running"; return; }
  [ -n "$(find "$BRAVO/triggers" -maxdepth 1 -name '*.json' -mmin -30 2>/dev/null | head -1)" ] && { echo "trigger waiting"; return; }
  bravo_busy 10 && { echo "pipeline active in last 10 min"; return; }
  bash "$G" check >/dev/null 2>&1 || { echo "foreground guard held"; return; }
  echo ""
}
why=$(busy_reason)
if [ -n "$why" ]; then echo "BUSY: $why - not started"; vlog "busy: $why"; exit 0; fi
bash "$G" acquire "$AGENT" >/dev/null 2>&1
trap 'bash "'"$G"'" release "'"$AGENT"'" >/dev/null 2>&1; rmdir "'"$VLOG/.lock.$AGENT"'" 2>/dev/null' EXIT
bravo_close_terminals >/dev/null 2>&1
rm -f "$ST"; T0=$(date +%s)
"$PRLCTL" exec "$VM" --current-user powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\_run_mobileevents_goldoff.ps1' -Stores "$STORES" -Mode "$MODE" 2>&1 | tail -1
s=""
while :; do
  sleep 20
  s=$(cat "$ST" 2>/dev/null)
  case "$s" in *COMPLETE*|*PAUSED*|*ABORT*) break ;; esac
  now=$(date +%s)
  if [ -z "$s" ] && [ $((now - T0)) -gt 300 ]; then s="ABORT never-started"; break; fi
  if [ $((now - T0)) -gt 1500 ]; then s="ABORT overran"; break; fi
done
case "$s" in *ABORT*)
  vm_ps_cmd "Get-CimInstance Win32_Process | Where-Object { \$_.CommandLine -like '*MobileEventsGoldOff.ahk*' } | ForEach-Object { Stop-Process -Id \$_.ProcessId -Force }" >/dev/null 2>&1
  HG=$(health_gate 600); s="$s health=$HG" ;;
esac
echo "end: $s"; vlog "end: $s"
ls -la "$OUT" | tail -8
exit 0
