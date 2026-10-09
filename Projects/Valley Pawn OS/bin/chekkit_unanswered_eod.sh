#!/bin/bash
# launchd wrapper — native chekkit-unanswered-eod-followup (Mac-first wave 1, 2026-10-08). Dormant unless fleet/state/native_live/chekkit-unanswered-eod-followup exists.
AGENT="chekkit-unanswered-eod-followup"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 60
"$PY" "$BIN/chekkit_unanswered.py" eod --send "$@" >> "$VLOG/$AGENT.log" 2>&1
