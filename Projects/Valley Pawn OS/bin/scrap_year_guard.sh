#!/bin/bash
# launchd wrapper — scrap year-file shrink guard (2026-10-20). Every 10 min + at load. NOT gated by native_live:
# it is a data protection (never posts, never pulls), not the replacement of a cloud task.
AGENT="scrap-year-guard"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 20
"$PY" "$BIN/scrap_year_guard.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
