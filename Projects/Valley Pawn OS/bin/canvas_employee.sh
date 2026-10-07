#!/bin/bash
# launchd wrapper — com.valleypawn.employee-canvas (Mon 09:24, native, 2026-10-06). Replaces Cowork `weekly-employee-perf-canvas-refresh`.
AGENT="weekly-employee-perf-canvas-refresh"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 60
"$PY" "$BIN/weekly_canvases.py" employee "$@" >> "$VLOG/$AGENT.log" 2>&1
