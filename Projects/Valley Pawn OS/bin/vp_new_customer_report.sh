#!/bin/bash
# launchd wrapper — native vp-new-customer-report (Mac-first wave 3 second pass, 2026-10-20). Day 3 07:00 ET.
# Dormant unless fleet/state/native_live/vp-new-customer-report exists (bin/vp_live.sh). --render runs call the .py directly.
AGENT="vp-new-customer-report"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 150
"$PY" "$BIN/vp_new_customer_report.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
