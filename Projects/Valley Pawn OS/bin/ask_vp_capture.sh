#!/bin/bash
# ask_vp_capture.sh — launchd wrapper for bin/ask_vp_capture.py (agent ask-vp-capture, nightly 22:00).
AGENT="ask-vp-capture"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
vp_lock "$AGENT" 120
"$PY" "$BIN/ask_vp_capture.py" "$@"
