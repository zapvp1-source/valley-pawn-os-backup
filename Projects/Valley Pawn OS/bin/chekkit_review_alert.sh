#!/bin/bash
# launchd wrapper — native chekkit-new-review-alert (Mac-first wave 1, 2026-10-08). Dormant unless fleet/state/native_live/chekkit-new-review-alert exists.
AGENT="chekkit-new-review-alert"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 50
"$PY" "$BIN/chekkit_review_alert.py" --send "$@" >> "$VLOG/$AGENT.log" 2>&1
