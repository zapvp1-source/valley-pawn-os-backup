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
# 2026-09-29: a flat 2400 s wait could never cover a 5-store jewelry pull (~16-20 min per store as of
# 9/28: CUL 20:53, HAR 21:09, LEX 21:30, then the host job timed out and ROA/WAY landed next morning).
# Scale with the store count: 20 min per store, never less than the old 40 min, capped at 2 h.
NST=$(echo "$STORES" | tr ',' '\n' | grep -c .); TO=$(( NST * 1200 )); [ $TO -lt 2400 ] && TO=2400; [ $TO -gt 7200 ] && TO=7200
bravo_run "$ID" "{\"name\":\"$REPORT\",\"stores\":[$SJ],\"date\":\"$DATE\"}" "$TO" || exit 1
echo "RESULT $BRAVO/results/$ID.result.json"; cat "$BRAVO/results/$ID.result.json" 2>/dev/null | head -c 2000; echo
