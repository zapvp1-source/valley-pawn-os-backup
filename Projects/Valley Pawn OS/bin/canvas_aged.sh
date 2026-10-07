#!/bin/bash
# launchd wrapper — com.valleypawn.aged-canvas (Mon 09:26, native, 2026-10-06). Replaces Cowork `weekly-aged-inventory-canvas-refresh`.
AGENT="weekly-aged-inventory-canvas-refresh"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 60
"$PY" "$BIN/weekly_canvases.py" aged "$@" >> "$VLOG/$AGENT.log" 2>&1
