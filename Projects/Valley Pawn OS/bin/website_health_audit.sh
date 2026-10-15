#!/bin/bash
# launchd wrapper — native weekly-website-health-audit (Mac-first wave 2, 2026-10-14). Dormant unless fleet/state/native_live/weekly-website-health-audit exists.
AGENT="weekly-website-health-audit"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 120
"$PY" "$BIN/website_health_audit.py" --send "$@" >> "$VLOG/$AGENT.log" 2>&1
