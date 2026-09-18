#!/bin/bash
# Native replacement for bravo-health-watchdog — 2026-09-17. Runs the health gate when the pipeline is idle.
AGENT=bravo-health-watchdog; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; vp_lock $AGENT 30
for i in 1 2 3; do bravo_busy 6 || break; vlog "pipeline busy — wait 3 min ($i/3)"; sleep 180; done
bravo_busy 6 && { vlog "still busy — exit silently"; exit 0; }
G="$BRAVO/_bravo_foreground_guard.sh"
bash "$G" check >/dev/null 2>&1 || { vlog "foreground guard BUSY — exit"; exit 0; }
bash "$G" acquire "$AGENT" >/dev/null 2>&1
trap 'bash "'"$G"'" release "'"$AGENT"'" >/dev/null 2>&1; rmdir "'"$VLOG/.lock.$AGENT"'" 2>/dev/null' EXIT
rm -f "$BRAVO/logs/_health_gate_status.txt"
( cd "$BRAVO" && LC_ALL=C LANG=C nohup bash ./bravo_health_gate.sh CUL >/dev/null 2>&1 < /dev/null & )
S=""; for i in $(seq 1 12); do sleep 25; S=$(cat "$BRAVO/logs/_health_gate_status.txt" 2>/dev/null); case "$S" in *PASS*|*FAIL*) break;; esac; done
vlog "health gate: ${S:-TIMEOUT}"
case "$S" in *PASS*) exit 0;; esac
ledger "bravo-health-watchdog" "Bravo health check did not pass (${S:-no result in 5 min}); the gate's own self-heal already ran." "no"
exit 1
