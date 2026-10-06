#!/bin/bash
# launchd wrapper — com.valleypawn.chekkit-review-invites (native, 2026-10-05).
AGENT="chekkit-weekly-review-requests"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 150
"$PY" "$BIN/chekkit_review_invites.py" --send "$@" >> "$VLOG/$AGENT.log" 2>&1
