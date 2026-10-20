#!/bin/bash
# launchd wrapper — native monthly-analytics-report (Mac-first wave 3, 2026-10-19). Dormant unless fleet/state/native_live/monthly-analytics-report exists (bin/vp_live.sh).
AGENT="monthly-analytics-report"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 150
"$PY" "$BIN/monthly_analytics_report.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
