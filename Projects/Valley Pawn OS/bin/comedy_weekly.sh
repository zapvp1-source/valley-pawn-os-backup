#!/bin/bash
# launchd wrapper — com.valleypawn.comedy-weekly (native, 2026-10-05).
AGENT="vp-comedy-reel-weekly"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 60
"$PY" "$BIN/comedy_weekly.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
