#!/bin/bash
# ivr_app_link_text.sh — launchd wrapper for bin/ivr_app_link_text.py (agent ivr-app-link-text).
# Every 60 s via com.valleypawn.ivr-app-link-text. Press 2 on the store phone menu -> app link text.
# Added 2026-11-09. --render previews without sending.
AGENT="ivr-app-link-text"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
RENDER=0; for a in "$@"; do [ "$a" = "--render" ] && RENDER=1; done
[ $RENDER -eq 0 ] && vp_lock "$AGENT" 5
"$PY" "$BIN/ivr_app_link_text.py" "$@"
