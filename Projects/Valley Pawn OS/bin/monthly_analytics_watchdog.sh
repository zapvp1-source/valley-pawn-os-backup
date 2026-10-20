#!/bin/bash
# launchd wrapper — native monthly-analytics-watchdog (Mac-first wave 3, 2026-10-19). Dormant unless fleet/state/native_live/monthly-analytics-watchdog exists (bin/vp_live.sh).
AGENT="monthly-analytics-watchdog"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 30
"$PY" "$BIN/monthly_analytics_watchdog.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
