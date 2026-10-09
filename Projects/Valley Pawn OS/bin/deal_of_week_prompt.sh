#!/bin/bash
# launchd wrapper — native vp-deal-of-week-monday-prompt (Mac-first wave 1, 2026-10-08). Dormant unless fleet/state/native_live/vp-deal-of-week-monday-prompt exists.
AGENT="vp-deal-of-week-monday-prompt"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 30
"$PY" "$BIN/deal_of_week_monday.py" prompt --send "$@" >> "$VLOG/$AGENT.log" 2>&1
