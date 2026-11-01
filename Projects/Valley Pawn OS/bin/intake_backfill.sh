#!/bin/bash
# launchd wrapper — com.valleypawn.intake-backfill (nightly 03:35, native, 2026-10-31).
# Self-healing coverage for Bravo intake-detail: any store-day in the trailing 14 days (yesterday back) with no
# single-day intake-detail CSV, or one without a real header row, is re-pulled through bravo_pull.sh (which
# waits out a busy pipeline and health-gates Bravo itself). At most MAX_DATES dates per night so it never
# collides with the 05:30 morning pull. Feeds gold_scorecard.py (bought step) and daily-intake-margin.
AGENT="intake-backfill"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 170
MAX_DATES="${MAX_DATES:-2}"; done_n=0
for i in $(seq 1 14); do
  d=$(date -v-${i}d +%Y-%m-%d)
  missing=""
  for st in CUL WAY HAR LEX ROA; do
    f="$BRAVO/output/${d}_to_${d}_${st}_intake-detail.csv"
    if [ ! -f "$f" ] || ! head -1 "$f" 2>/dev/null | grep -q "Ticket Kind"; then missing="$missing,$st"; fi
  done
  missing="${missing#,}"
  [ -z "$missing" ] && continue
  vlog "backfill $d stores=$missing"
  "$BIN/bravo_pull.sh" intake-detail "$d..$d" "$missing" "intake-backfill-$d" >> "$VLOG/$AGENT.log" 2>&1
  vlog "backfill $d rc=$?"
  done_n=$((done_n+1)); [ "$done_n" -ge "$MAX_DATES" ] && break
done
vlog "intake_backfill finished dates_pulled=$done_n"
