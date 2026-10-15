#!/bin/bash
# launchd wrapper — native health-weekly-digest (Mac-first wave 2, 2026-10-14). Dormant unless fleet/state/native_live/health-weekly-digest exists.
AGENT="health-weekly-digest"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 30
"$PY" "$BIN/health_weekly_digest.py" --send "$@" >> "$VLOG/$AGENT.log" 2>&1
