#!/bin/bash
# launchd wrapper — com.valleypawn.winback-texts (native, 2026-10-05).
AGENT="forfeiture-winback-texts-weekly"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 60
"$PY" "$BIN/winback_texts.py" --send "$@" >> "$VLOG/$AGENT.log" 2>&1
