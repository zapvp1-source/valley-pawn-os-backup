#!/bin/bash
# launchd wrapper — com.valleypawn.nics-monthly, 1st of month 09:30 (native, 2026-10-02).
AGENT="nics-monthly-ranking"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 150
"$PY" "$BIN/nics_monthly.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
