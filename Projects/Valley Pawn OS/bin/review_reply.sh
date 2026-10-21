#!/bin/bash
# launchd wrapper — com.valleypawn.review-reply, 19:30 daily. Native replacement for the Cowork task
# nightly-chekkit-review-responses (comms review 2026-10-20). Dormant unless
# fleet/state/native_live/nightly-chekkit-review-responses exists (create it after one clean --render on a signed-in profile).
AGENT="nightly-chekkit-review-responses"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 60
"$PY" "$BIN/review_reply.py" --send "$@" >> "$VLOG/$AGENT.log" 2>&1
