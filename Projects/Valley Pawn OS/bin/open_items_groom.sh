#!/bin/bash
# launchd wrapper — com.valleypawn.open-items-groom, nightly 03:20 (2026-10-23). See bin/open_items_groom.py.
AGENT="open-items-groom"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 10
"$PY" "$BIN/open_items_groom.py" --apply "$@" >> "$VLOG/$AGENT.log" 2>&1
