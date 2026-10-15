#!/bin/bash
# launchd wrapper — native vp-publer-analytics-friday (Mac-first wave 2, 2026-10-14). Dormant unless fleet/state/native_live/vp-publer-analytics-friday exists.
AGENT="vp-publer-analytics-friday"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 60
"$PY" "$BIN/publer_friday.py" --send "$@" >> "$VLOG/$AGENT.log" 2>&1
