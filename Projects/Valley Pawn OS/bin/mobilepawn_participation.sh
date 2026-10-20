#!/bin/bash
# launchd wrapper — native monthly-mobilepawn-participation (Mac-first wave 3, 2026-10-19). 1st–3rd 09:15 ET, posts once.
# Dormant unless fleet/state/native_live/monthly-mobilepawn-participation exists (bin/vp_live.sh).
AGENT="monthly-mobilepawn-participation"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 150
"$PY" "$BIN/mobilepawn_participation.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
