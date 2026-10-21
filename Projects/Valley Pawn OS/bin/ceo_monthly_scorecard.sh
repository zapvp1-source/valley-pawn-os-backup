#!/bin/bash
# launchd wrapper — native ceo-monthly-scorecard (Mac-first wave 3 second pass, 2026-10-20). Day 3 12:00 ET.
# Dormant unless fleet/state/native_live/ceo-monthly-scorecard exists (bin/vp_live.sh). --render runs call the .py directly.
AGENT="ceo-monthly-scorecard"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 90
"$PY" "$BIN/ceo_monthly_scorecard.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
