#!/bin/bash
# launchd wrapper — native daily-clockin-check (Mac-first, 2026-10-18). Mon–Sat 10:15 ET -> #general.
# Dormant unless fleet/state/native_live/daily-clockin-check exists (vp_live.sh).
AGENT="daily-clockin-check"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 30
"$PY" "$BIN/clockin_check.py" --send "$@" >> "$VLOG/$AGENT.log" 2>&1
