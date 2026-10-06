#!/bin/bash
# launchd wrapper — com.valleypawn.deal-of-week-pick (native, 2026-10-05).
AGENT="vp-deal-of-week-monday-pick"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 60
"$PY" "$BIN/deal_of_week_pick.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
