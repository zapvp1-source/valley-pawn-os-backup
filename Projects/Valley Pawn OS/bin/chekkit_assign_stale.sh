#!/bin/bash
# launchd wrapper — com.valleypawn.chekkit-assign-stale, every 5 min: customer texts unanswered 10+ min in store hours are assigned to the store manager in Chekkit (API). Added 2026-10-21.
AGENT="chekkit-assign-stale"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 10
"$PY" "$BIN/chekkit_ops.py" assign-stale "$@" >> "$VLOG/$AGENT.log" 2>&1
