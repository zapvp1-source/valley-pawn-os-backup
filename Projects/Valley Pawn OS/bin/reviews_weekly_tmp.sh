#!/bin/bash
# launchd wrapper — com.valleypawn.reviews-weekly (native, 2026-10-05).
AGENT="review-obtained-last-week"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 60
"$PY" "$BIN/reviews_weekly_tmp.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
