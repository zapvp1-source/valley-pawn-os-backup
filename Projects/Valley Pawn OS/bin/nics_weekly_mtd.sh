#!/bin/bash
# launchd wrapper — com.valleypawn.nics-weekly-mtd (Mon 09:30, native, 2026-10-05). Replaces Cowork `nics-weekly-mtd-ranking`.
AGENT="nics-weekly-mtd-ranking"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 150
"$PY" "$BIN/nics_weekly_mtd.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
