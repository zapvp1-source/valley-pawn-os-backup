#!/bin/bash
# launchd wrapper — native northwest-registered-agent-daily-check (Mac-first, 2026-10-18). Daily 08:49 ET.
# Dormant unless fleet/state/native_live/northwest-registered-agent-daily-check exists (vp_live.sh).
AGENT="northwest-registered-agent-daily-check"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 30
"$PY" "$BIN/northwest_check.py" --send "$@" >> "$VLOG/$AGENT.log" 2>&1
