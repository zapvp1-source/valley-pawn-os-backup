#!/bin/bash
# launchd wrapper — native daily-cloudcover-check (Mac-first, 2026-10-14). Dormant unless fleet/state/native_live/daily-cloudcover-check exists.
AGENT="daily-cloudcover-check"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 30
"$PY" "$BIN/cloudcover_check.py" --send "$@" >> "$VLOG/$AGENT.log" 2>&1
