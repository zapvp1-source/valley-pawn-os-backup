#!/bin/bash
# bravo_pull.sh <report> <date|from..to> <STORES,CSV> [id] [--no-gate]
# Allow-listed host primitive for Cowork tasks that lost osascript: health gate, drop ONE trigger,
# wait for the result (self-heal once), print the result path. Exit 0 = result written.
#   bravo_pull.sh safe-register-journal 2026-09-17 CUL,HAR,LEX,ROA,WAY
#   bravo_pull.sh jewelry-case-counts-v2 2026-09-17 CUL jewelry-onhand-2026-09-17-CUL
AGENT=bravo-pull; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
REPORT="$1"; DATE="$2"; STORES="$3"; ID="${4:-${REPORT}-$(date +%Y-%m-%dT%H-%M-%S)}"
[ -z "$REPORT" ] || [ -z "$DATE" ] || [ -z "$STORES" ] && { echo "usage: bravo_pull.sh <report> <date> <STORES,CSV> [id]"; exit 2; }
case "$ID" in --no-gate) ID="${REPORT}-$(date +%Y-%m-%dT%H-%M-%S)";; esac
for i in 1 2 3; do bravo_busy 3 || break; vlog "pipeline busy — wait 60s ($i/3)"; sleep 60; done
[ "$5" = "--no-gate" ] || vlog "health gate: $(health_gate 600)"
SJ=$(echo "$STORES" | tr ',' '\n' | sed 's/.*/"&"/' | paste -sd, -)
bravo_run "$ID" "{\"name\":\"$REPORT\",\"stores\":[$SJ],\"date\":\"$DATE\"}" 2400 || exit 1
echo "RESULT $BRAVO/results/$ID.result.json"; cat "$BRAVO/results/$ID.result.json" 2>/dev/null | head -c 2000; echo
