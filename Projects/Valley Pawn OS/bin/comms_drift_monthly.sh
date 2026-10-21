#!/bin/bash
# launchd wrapper — native vp-comms-drift-monthly-check (Mac-first wave 3 second pass, 2026-10-20). Day 3 08:00 ET.
# Dormant unless fleet/state/native_live/vp-comms-drift-monthly-check exists (bin/vp_live.sh). --render runs call the .py directly.
AGENT="vp-comms-drift-monthly-check"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 60
"$PY" "$BIN/comms_drift_monthly.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
