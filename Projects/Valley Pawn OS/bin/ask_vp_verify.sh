#!/bin/bash
# ask_vp_verify.sh — launchd wrapper for bin/ask_vp_verify.py (agent ask-vp-verify, Mondays 09:00).
AGENT="ask-vp-verify"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 30
"$PY" "$BIN/ask_vp_verify.py" "$@"
