#!/bin/bash
# launchd wrapper — native entity-compliance-check (Mac-first wave 3 second pass, 2026-10-20). Day 1 09:00 ET.
# Dormant unless fleet/state/native_live/entity-compliance-check exists (bin/vp_live.sh). --render runs call the .py directly.
AGENT="entity-compliance-check"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 60
"$PY" "$BIN/entity_compliance_monthly.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
