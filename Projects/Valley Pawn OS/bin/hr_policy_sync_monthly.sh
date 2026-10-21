#!/bin/bash
# launchd wrapper — native vp-hr-policy-monthly-sync (Mac-first wave 3 second pass, 2026-10-20). Day 1 08:35 ET.
# Dormant unless fleet/state/native_live/vp-hr-policy-monthly-sync exists (bin/vp_live.sh). --render runs call the .py directly.
AGENT="vp-hr-policy-monthly-sync"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 60
"$PY" "$BIN/hr_policy_sync_monthly.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
