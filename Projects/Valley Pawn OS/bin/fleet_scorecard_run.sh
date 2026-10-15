#!/bin/bash
# launchd wrapper — com.valleypawn.fleet-scorecard, daily 07:15 ET (native, 2026-10-14).
# The ONE morning "finish line" DM to Joshua: yesterday's reports — landed / once / on time.
AGENT="fleet-scorecard"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 30
"$PY" "$BIN/fleet_scorecard.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
