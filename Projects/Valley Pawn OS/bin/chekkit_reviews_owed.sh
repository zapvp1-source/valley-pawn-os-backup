#!/bin/bash
# launchd wrapper — com.valleypawn.chekkit-reviews-owed, 19:05 daily: reviews still owed a reply per store (Chekkit API) for the 19:20 texting scorecard. Added 2026-10-21.
AGENT="chekkit-reviews-owed"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 20
"$PY" "$BIN/chekkit_ops.py" reviews-owed "$@" >> "$VLOG/$AGENT.log" 2>&1
