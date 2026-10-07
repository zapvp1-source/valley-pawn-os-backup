#!/bin/bash
# launchd wrapper — com.valleypawn.layaway-yield-weekly (Mon 11:15, native, 2026-10-06). Replaces Cowork `layaway-yield-weekly`.
AGENT="layaway-yield-weekly"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 60
"$PY" "$BIN/layaway_yield_weekly.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
