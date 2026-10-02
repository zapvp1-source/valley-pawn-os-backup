#!/bin/bash
# bravo_map_run.sh [full|smoke] -- orchestrates BravoMapper.ahk (the read-only "map all of Bravo" crawler).
# Additive 2026-09-30. Runs from the native agent com.valleypawn.bravo-map-oneshot (nightly 22:30 + Sun 07:00)
# until the map is COMPLETE, and from the host queue for a smoke test. Allow-listed.
#
# Safety contract (Bravo contention rules, bravo-context skill):
#   - waits until NO pipeline work is active (month-end prestage, pulls, watcher logs, fresh triggers,
#     foreground guard) before touching Bravo; gives up quietly if no clear window before the deadline
#   - holds the foreground guard for the whole run (refreshed every minute; guard goes stale at 45 min)
#   - hard deadline: 01:40 on weeknights (2:10 AM monthly pull), 11:45 on Sunday mornings
#   - the crawler checkpoints every step and always returns Bravo to the Dashboard; if it hangs, stalls
#     or overruns it is killed and the standard health gate puts Bravo back on a Dashboard
#   - silent (Rule 16): progress goes to output/bravo_map/RUN_LOG.md; one ledger row only if recovery fails
AGENT=bravo-map; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; vp_lock $AGENT 420
MODE="${1:-full}"
MAP="$BRAVO/output/bravo_map"; ST="$MAP/_status.txt"; RUNLOG="$MAP/RUN_LOG.md"; mkdir -p "$MAP"
G="$BRAVO/_bravo_foreground_guard.sh"

if [ "$MODE" = full ] && [ -f "$MAP/_COMPLETE" ]; then vlog "map already complete - nothing to do"; exit 0; fi

H=$(date +%H); DOW=$(date +%u)
if [ "$MODE" = smoke ]; then DL=$(date -v+60M +%Y%m%d%H%M%S)   # smoke stops itself after 3 steps
elif [ "$H" -ge 18 ]; then DL="$(date -v+1d +%Y%m%d)014000"
elif [ "$H" -lt 1 ]; then DL="$(date +%Y%m%d)014000"
elif [ "$DOW" = 7 ] && [ "$H" -lt 11 ]; then DL="$(date +%Y%m%d)114500"
else vlog "outside a mapping window (hour $H) - exit"; exit 0; fi
DLE=$(date -j -f %Y%m%d%H%M%S "$DL" +%s)
MINLEFT=1800; [ "$MODE" = smoke ] && MINLEFT=300
vlog "start mode=$MODE deadline=$DL"

# ---- wait for a genuinely idle Bravo
busy_reason() {
  pgrep -f "monthly_prestage_runner.py" >/dev/null && { echo "month-end prestage running"; return; }
  pgrep -f "bravo_pull.sh|monday_pull.sh|morning_pull.sh|daily_report.sh|scrap_closeout_run.sh|forfeiture_winback_weekly.sh|bravo_relaunch.sh|bravo_ensure_healthy|funds_verification.sh" >/dev/null && { echo "a Bravo job is running on the host"; return; }
  [ -n "$(find "$BRAVO/triggers" -maxdepth 1 -name '*.json' -mmin -30 2>/dev/null | head -1)" ] && { echo "trigger waiting"; return; }
  bravo_busy 10 && { echo "pipeline active in last 10 min"; return; }
  [ -n "$(find "$BRAVO/logs" -maxdepth 1 -name '*.log' -mmin -5 ! -name 'bravomap-*' ! -name '_hg_native.log' 2>/dev/null | head -1)" ] && { echo "watcher log still being written"; return; }
  bash "$G" check >/dev/null 2>&1 || { echo "foreground guard held"; return; }
  echo ""
}
while :; do
  now=$(date +%s)
  if [ $((DLE - now)) -lt $MINLEFT ]; then vlog "no idle window before deadline - exit, next window will resume"; echo "- $(date '+%F %H:%M') skipped: Bravo never idle before the deadline" >> "$RUNLOG"; exit 0; fi
  why=$(busy_reason); [ -z "$why" ] && break
  vlog "waiting: $why"; sleep 180
done

# ---- launch
kill_mapper() { vm_ps_cmd "Get-CimInstance Win32_Process | Where-Object { \$_.CommandLine -like '*BravoMapper.ahk*' } | ForEach-Object { Stop-Process -Id \$_.ProcessId -Force }; 'killed'" 2>/dev/null | tail -1; }
bash "$G" acquire "$AGENT" >/dev/null 2>&1
trap 'bash "'"$G"'" release "'"$AGENT"'" >/dev/null 2>&1; rmdir "'"$VLOG/.lock.$AGENT"'" 2>/dev/null' EXIT
bravo_close_terminals >/dev/null 2>&1
D0=$(cat "$MAP/_done.txt" 2>/dev/null | wc -l | tr -d ' ')
# v2 2026-10-01: up to 3 relaunches per window when an abort was recovered (health PASS) and >30 min
# remain -- the 9/30 run lost the rest of the night to one stranded screen at 22:54.
RELAUNCH=0; HG=""
while :; do
  rm -f "$ST"
  T0=$(date +%s)
  "$PRLCTL" exec "$VM" --current-user powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\_run_bravomapper.ps1' -Deadline "$DL" -Mode "$MODE" -Store CUL 2>&1 | tail -1 | while read -r l; do vlog "launch: $l"; done

  # ---- monitor
  HARD=$((DLE + 900)); s=""
  while :; do
    sleep 60
    bash "$G" acquire "$AGENT" >/dev/null 2>&1          # refresh ownership (guard treats >45 min as stale)
    s=$(cat "$ST" 2>/dev/null)
    case "$s" in *COMPLETE*|*DONE-SMOKE*|*PAUSED-DEADLINE*|*ABORT*) break ;; esac
    now=$(date +%s); m=$(stat -f %m "$ST" 2>/dev/null || echo 0)
    if [ -z "$s" ] && [ $((now - T0)) -gt 600 ]; then s="ABORT never-started (see logs/bravomap-*.log)"; kill_mapper >/dev/null; break; fi
    if [ -n "$s" ] && [ $((now - m)) -gt 900 ]; then s="ABORT stalled: $s"; vlog "kill: $(kill_mapper)"; break; fi
    if [ "$now" -gt "$HARD" ]; then s="ABORT overran deadline"; vlog "kill: $(kill_mapper)"; break; fi
  done
  vlog "crawler ended: $s"

  # ---- recovery (any abnormal end): standard health gate puts Bravo back on a Dashboard
  case "$s" in *ABORT*) ;; *) break ;; esac
  HG=$(health_gate 600); vlog "health gate: $HG"
  case "$HG" in *PASS*) ;; *) ledger "$AGENT" "The overnight Bravo mapping run stopped early and Bravo did not confirm healthy afterwards." "no"; break ;; esac
  echo "- $(date '+%F %H:%M') recovered from '$s' (health=$HG)" >> "$RUNLOG"
  case "$s" in *never-started*) break ;; esac
  RELAUNCH=$((RELAUNCH + 1))
  [ $RELAUNCH -gt 3 ] && break
  [ $((DLE - $(date +%s))) -lt 1800 ] && break
  [ -n "$(busy_reason)" ] && { vlog "pipeline busy after recovery - stop for tonight"; break; }
  vlog "relaunching crawler ($RELAUNCH/3)"
done

# ---- progress + compile
D1=$(cat "$MAP/_done.txt" 2>/dev/null | wc -l | tr -d ' '); F1=$(sort -u "$MAP/_fail.txt" 2>/dev/null | wc -l | tr -d ' ')
case "$s" in *COMPLETE*) touch "$MAP/_COMPLETE" ;; esac
echo "- $(date '+%F %H:%M') mode=$MODE end='$s' steps_done_total=$D1 (+$((D1 - D0)) this run) failed_keys=$F1 ${HG:+health=$HG}" >> "$RUNLOG"
"$PY" "$BIN/bravo_map_compile.py" >> "$VLOG/$AGENT.log" 2>&1 && vlog "compiled BRAVO_MAP.md"
exit 0
