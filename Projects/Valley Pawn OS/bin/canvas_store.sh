#!/bin/bash
# launchd wrapper — com.valleypawn.store-canvas (Mon 09:28, native, 2026-10-06). Replaces Cowork `weekly-store-perf-canvas-refresh`.
AGENT="weekly-store-perf-canvas-refresh"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 60
"$PY" "$BIN/weekly_canvases.py" store "$@" >> "$VLOG/$AGENT.log" 2>&1
