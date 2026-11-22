#!/bin/bash
# ebay_takedown_watch.sh — native agent com.valleypawn.ebay-takedown-watch (built 2026-11-21, eBay Desk).
# WATCH ONLY: pulls Bravo's company-wide "sold today" (cell sold-today-all, ~90 s, no store switch) and logs which
# live eBay listings the takedown loop WOULD end. It ends nothing and writes nothing to eBay or Bravo.
# Never self-heals Bravo: if the pipeline is busy or the pull does not come back in 6 min, it skips this round.
# Silent (Rule 16): results go to eBay/desk/out/takedown_watch.jsonl and the agent log only.
AGENT="ebay-takedown-watch"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 15
TODAY=$(date +%Y-%m-%d)
[ -z "$(open_stores "$TODAY")" ] && exit 0
H=$((10#$(date +%H))); { [ $H -lt 10 ] || [ $H -ge 18 ]; } && exit 0
if bravo_busy 3 || [ -n "$(ls "$BRAVO"/triggers/*.json 2>/dev/null | head -1)" ] || ! bash "$BRAVO/_bravo_foreground_guard.sh" check >/dev/null 2>&1; then
  vlog "skip: Bravo busy"; exit 0
fi
ID="ebaydesk-takedown-watch-$(date +%Y%m%dT%H%M)"
printf '{"id":"%s","requested_at":"%s","reports":[{"name":"sold-today-all","stores":["ALL"],"date":"%s..%s"}]}' "$ID" "$(date +%Y-%m-%dT%H:%M:%S%z)" "$TODAY" "$TODAY" > "$BRAVO/triggers/staging/$ID.json"
mv "$BRAVO/triggers/staging/$ID.json" "$BRAVO/triggers/$ID.json"
T0=$(date +%s)
while [ ! -f "$BRAVO/results/$ID.result.json" ] && [ $(( $(date +%s) - T0 )) -lt 360 ]; do sleep 10; done
if [ ! -f "$BRAVO/results/$ID.result.json" ]; then
  rm -f "$BRAVO/triggers/$ID.json"          # still unclaimed: take it back so rounds never pile up
  vlog "skip: no result for $ID in 6 min"; exit 0
fi
CSV="$BRAVO/output/${TODAY}_to_${TODAY}_ALL_sold-today-all.csv"
grep -q '"status": *"success"' "$BRAVO/results/$ID.result.json" && [ -f "$CSV" ] || { vlog "skip: pull not successful ($ID)"; exit 0; }
DST="$HOME/Documents/Claude/Projects/eBay/desk/out/bravo_pulls"; mkdir -p "$DST"
mv "$CSV" "$DST/sold-today-all_latest.csv"
vlog "pull $(( $(date +%s) - T0 ))s: $("$PY" "$HOME/Documents/Claude/Projects/eBay/desk/takedown_watch.py" "$DST/sold-today-all_latest.csv" 2>&1 | tail -4 | tr '\n' ' ')"
