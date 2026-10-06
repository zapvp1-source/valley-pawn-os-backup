#!/bin/bash
# launchd wrapper — com.valleypawn.bonus-pace (native, 2026-10-05; replaces Cowork bonus-pace-monday).
AGENT="bonus-pace-monday"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 60
"$PY" "$BIN/bonus_pace.py"  "$@" >> "$VLOG/$AGENT.log" 2>&1
