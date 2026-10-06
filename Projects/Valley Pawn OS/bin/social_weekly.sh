#!/bin/bash
# launchd wrapper — com.valleypawn.social-weekly (native, 2026-10-05).
AGENT="vp-content-batch-weekly"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 120
"$PY" "$BIN/social_weekly.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
