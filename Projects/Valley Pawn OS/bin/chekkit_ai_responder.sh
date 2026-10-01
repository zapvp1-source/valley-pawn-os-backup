#!/bin/bash
# chekkit_ai_responder.sh — launchd wrapper for bin/chekkit_ai_responder.py (agent chekkit-ai-responder).
# Runs every 60 s via com.valleypawn.chekkit-ai-responder. Mode (shadow/live) lives in
# fleet/chekkit_ai_config.json. Pass --render or --selftest for a preview. Added 2026-09-30 (Joshua).
AGENT="chekkit-ai-responder"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
LOCKIT=1; for a in "$@"; do case "$a" in --render|--selftest|--text) LOCKIT=0 ;; esac; done
[ $LOCKIT -eq 1 ] && vp_lock "$AGENT" 5
"$PY" "$BIN/chekkit_ai_responder.py" "$@"
