#!/bin/bash
# launchd wrapper — com.valleypawn.layaway-canvas (Mon 09:22, native, 2026-10-06). Replaces Cowork `weekly-layaway-review-canvas-refresh`.
AGENT="weekly-layaway-review-canvas-refresh"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 60
"$PY" "$BIN/weekly_canvases.py" layaway "$@" >> "$VLOG/$AGENT.log" 2>&1
