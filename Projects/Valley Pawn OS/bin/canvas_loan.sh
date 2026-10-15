#!/bin/bash
# launchd wrapper — com.valleypawn.loan-canvas (Mon 09:20, native, 2026-10-06). Replaces Cowork `weekly-loan-review-canvas-refresh`.
# RETIRED 2026-10-14 (Joshua: the 75-day loan review goes away). Exits without touching the canvas.
exit 0
AGENT="weekly-loan-review-canvas-refresh"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 60
"$PY" "$BIN/weekly_canvases.py" loan "$@" >> "$VLOG/$AGENT.log" 2>&1
