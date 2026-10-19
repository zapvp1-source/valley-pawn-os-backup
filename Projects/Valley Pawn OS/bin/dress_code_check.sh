#!/bin/bash
# launchd wrapper — native daily-dress-code-check (Mac-first, 2026-10-18). Mon-Sat 10:30 ET.
# Dormant unless fleet/state/native_live/daily-dress-code-check exists (vp_live.sh).
AGENT="daily-dress-code-check"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 30
"$PY" "$BIN/dress_code_check.py" --send "$@" >> "$VLOG/$AGENT.log" 2>&1
