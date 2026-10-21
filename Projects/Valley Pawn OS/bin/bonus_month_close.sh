#!/bin/bash
# launchd wrapper — native bonus-month-close (Mac-first wave 3 second pass, 2026-10-20). Day 10 09:00 ET.
# Dormant unless fleet/state/native_live/bonus-month-close exists (bin/vp_live.sh). --render runs call the .py directly.
AGENT="bonus-month-close"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 90
"$PY" "$BIN/bonus_month_close.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
