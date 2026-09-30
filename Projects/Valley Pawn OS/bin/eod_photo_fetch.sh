#!/bin/bash
# launchd wrapper — com.valleypawn.eod-photo-fetch, Mon-Sat 20:15 (after the ~18:15-18:35 sheet posts,
# before jewelry-onhand-nightly-pull at 20:30). Also fetches YESTERDAY for the morning catch-up.
AGENT="eod-photo-fetch"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
"$PY" "$BIN/eod_photo_fetch.py" >> "$VLOG/$AGENT.log" 2>&1 || ledger "$AGENT" "Tonight's end-of-day count-sheet photos could not be downloaded for the jewelry count." "no"
"$PY" "$BIN/eod_photo_fetch.py" "$(date -v-1d +%Y-%m-%d)" >> "$VLOG/$AGENT.log" 2>&1
exit 0
