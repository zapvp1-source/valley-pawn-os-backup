#!/bin/bash
# ask_vp_responder.sh — launchd wrapper for bin/ask_vp_responder.py (agent ask-vp, Ask Valley Pawn).
# Runs every 15 s via com.valleypawn.ask-vp. Mode (SHADOW/LIVE) and channel live in
# Projects/Ask Valley Pawn/config.json. Pass --ask / --selftest / --status for a manual run (no lock).
AGENT="ask-vp"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
LOCKIT=1; for a in "$@"; do case "$a" in --ask|--selftest|--status) LOCKIT=0 ;; esac; done
[ $LOCKIT -eq 1 ] && vp_lock "$AGENT" 5
"$PY" "$BIN/ask_vp_responder.py" "$@"
