#!/bin/bash
# launchd wrapper — native monthly-eom-recap (Mac-first wave 3 second pass, 2026-10-20). Day 1 10:30 ET.
# Dormant unless fleet/state/native_live/monthly-eom-recap exists (bin/vp_live.sh). --render runs call the .py directly.
AGENT="monthly-eom-recap"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 120
"$PY" "$BIN/monthly_eom_recap.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
