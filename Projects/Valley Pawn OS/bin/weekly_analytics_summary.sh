#!/bin/bash
# launchd wrapper — native weekly-analytics-summary (2026-10-14, Google re-grant prep). Dormant unless fleet/state/native_live/weekly-analytics-summary exists.
AGENT="weekly-analytics-summary"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 30
"$PY" "$BIN/weekly_analytics_summary.py" --send "$@" >> "$VLOG/$AGENT.log" 2>&1
