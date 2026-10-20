#!/bin/bash
# launchd wrapper — native monthly-ebay-ratings-sweep, post half (Mac-first wave 3, 2026-10-19). 1st of month 10:00 ET.
# Dormant unless fleet/state/native_live/monthly-ebay-ratings-sweep exists (bin/vp_live.sh).
# Data half = the existing native com.valleypawn.ebay-ratings-pull (09:45, bin/ebay_ratings_pull.sh ->
# eBay/ebay-ratings-sweep-<YYYY-MM>.md). If that file is missing or shows a PULL FAILED store, run the pull once
# more here (SKILL step 1 retry), then post the digest (bin/ebay_ratings_post.py).
AGENT="monthly-ebay-ratings-sweep"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
if [ "$1" = "--render" ]; then shift; "$PY" "$BIN/ebay_ratings_post.py" --render "$@"; exit $?; fi
vp_live_gate "$AGENT"
vp_lock "$AGENT" 60
F="$HOME/Documents/Claude/Projects/eBay/ebay-ratings-sweep-$(date +%Y-%m).md"
if [ ! -s "$F" ] || grep -q 'PULL FAILED' "$F"; then vlog "ratings file missing/partial — running the pull once"; bash "$BIN/ebay_ratings_pull.sh" >> "$VLOG/$AGENT.log" 2>&1; fi
"$PY" "$BIN/ebay_ratings_post.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
