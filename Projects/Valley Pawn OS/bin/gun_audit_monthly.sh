#!/bin/bash
# launchd wrapper — native monthly-gun-audit-report (Mac-first wave 3 second pass, 2026-10-20). Day 16 02:30 ET.
# Dormant unless fleet/state/native_live/monthly-gun-audit-report exists (bin/vp_live.sh). --render runs call the .py directly.
AGENT="monthly-gun-audit-report"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 90
"$PY" "$BIN/gun_audit_monthly.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
