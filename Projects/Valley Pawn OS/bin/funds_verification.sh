#!/bin/bash
# launchd wrapper — com.valleypawn.funds-verification, 18:30 daily. Native replacement for the Cowork task
# daily-funds-verification (2026-09-30). Skips itself if the Cowork run already saved a complete report.
AGENT="daily-funds-verification"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 150
"$PY" "$BIN/funds_verification.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
