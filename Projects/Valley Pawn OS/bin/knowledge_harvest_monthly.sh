#!/bin/bash
# launchd wrapper — native vp-knowledge-harvest-monthly (built 2026-10-22). Day 22 06:30 ET, before the 25th Policy Day cutoff.
# Dormant unless fleet/state/native_live/vp-knowledge-harvest-monthly exists (bin/vp_live.sh). --render runs call the .py directly.
AGENT="vp-knowledge-harvest-monthly"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 240
"$PY" -u "$BIN/knowledge_harvest_monthly.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
