#!/bin/bash
# launchd wrapper — com.valleypawn.reviews-weekly (proposed: Mondays 09:00 ET; NOT installed yet).
# Native replacement for Cowork review-obtained-last-week + google-reviews-post-watchdog (2026-10-05).
AGENT="review-obtained-last-week"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 30
"$PY" "$BIN/reviews_weekly.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
