#!/bin/bash
# wh_backfill.sh -- native agent com.valleypawn.wh-backfill (built 2026-11-27, Joshua approved: "we need ALL the data").
# Type A (drops triggers; queued by the watcher). Works down "Bravo Warehouse/backfill_queue.txt" a few windows per
# run (read-only Bravo cells only), then rebuilds the warehouse. Sundays (stores closed) 9:20, 10:20, 11:20 AM, 3:20, 6:30, 7:30, 8:30, 9:30 PM -- clear of winback 12:30,
# GL 1:10, birthday list 2:40, Monday pull 4:30. Daily 3:05 AM: rebuild only, no Bravo contact.
# Queue line:  <cell> <YYYY-MM-DD..YYYY-MM-DD> <STORES,CSV>     (# = comment)
# Done marker per line: fleet/state/wh-backfill/done/<id>. Three failed tries -> parked in .../failed/ and ONE
# ledger row. Silent (Rule 16). Args: [max windows this run] [--rebuild-only]
AGENT="wh-backfill"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 100
WH="$HOME/Documents/Claude/Projects/Bravo Warehouse"
ST="$OS_DIR/fleet/state/wh-backfill"; mkdir -p "$ST/done" "$ST/failed" "$ST/tries"
MAX="${1:-0}"
# Scheduled runs: Sunday = 6 windows; any other day = rebuild only (weeknights are full: relaunch 4:00, reminders 4:40).
# 2026-11-27: plus every night at 11:20 PM, 4 windows (after loan reminders 10:40 PM, done well before the 1:45 AM inventory pull).
if [ "$MAX" = "0" ]; then H=$(date +%H); if [ "$H" = "23" ]; then MAX=4; elif [ "$(date +%u)" = "7" ]; then MAX=6; else MAX=-1; fi; fi
N=0
if [ "$1" != "--rebuild-only" ] && [ "$MAX" != "-1" ] && [ ! -f "$ST/PAUSED" ] && [ -f "$WH/backfill_queue.txt" ]; then
  while read -r CELL RANGE STORES _; do
    case "$CELL" in ""|\#*) continue;; esac
    [ -z "$RANGE" ] || [ -z "$STORES" ] && continue
    ID="wh-$CELL-${RANGE%%..*}-$(echo "$STORES" | tr ',' '-')"
    [ -f "$ST/done/$ID" ] || [ -f "$ST/failed/$ID" ] && continue
    [ $N -ge $MAX ] && break
    N=$((N+1))
    T=$(cat "$ST/tries/$ID" 2>/dev/null || echo 0); T=$((T+1)); echo $T > "$ST/tries/$ID"
    RID="$ID-t$T"
    vlog "pull $CELL $RANGE $STORES (try $T)"
    bash "$BIN/bravo_pull.sh" "$CELL" "$RANGE" "$STORES" "$RID" < /dev/null >> "$VLOG/$AGENT.log" 2>&1
    if grep -q '"status": *"success"' "$BRAVO/results/$RID.result.json" 2>/dev/null && ! grep -q '"status": *"error"' "$BRAVO/results/$RID.result.json"; then
      date > "$ST/done/$ID"; vlog "done $ID"
    elif [ $T -ge 3 ]; then
      date > "$ST/failed/$ID"
      ledger "$AGENT" "History pull $CELL $RANGE ($STORES) failed three times and was parked; the rest of the backfill continues." "no"
    else
      vlog "not complete: $ID (will retry)"
    fi
    sleep 20
  done < "$WH/backfill_queue.txt"
fi
"$PY" "$WH/bin/build_warehouse.py" >> "$VLOG/$AGENT.log" 2>&1; vlog "end: windows=$N rebuild rc=$?"
exit 0
