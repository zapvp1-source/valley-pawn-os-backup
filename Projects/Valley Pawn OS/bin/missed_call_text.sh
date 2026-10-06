#!/bin/bash
# missed_call_text.sh — launchd wrapper for bin/missed_call_text.py (agent missed-call-text).
# Runs every 60 s via com.valleypawn.missed-call-text. The Python does all the work and exits
# immediately outside the 08:00-21:00 ET send window. Pass --render to preview without sending.
# Added 2026-09-24 (Joshua: "build it"). Shipped NOT installed — see CHANGELOG 2026-09-24.
AGENT="missed-call-text"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
RENDER=0; for a in "$@"; do [ "$a" = "--render" ] && RENDER=1; done
[ $RENDER -eq 0 ] && vp_lock "$AGENT" 5
"$PY" "$BIN/missed_call_text.py" "$@"
