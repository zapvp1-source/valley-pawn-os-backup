#!/bin/bash
# launchd wrapper — native monthly-employee-sales-rankings (Mac-first wave 3, 2026-10-19). 1st of month 02:00 ET.
# Dormant unless fleet/state/native_live/monthly-employee-sales-rankings exists (bin/vp_live.sh).
AGENT="monthly-employee-sales-rankings"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 150
"$PY" "$BIN/monthly_employee_rankings.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
