#!/bin/bash
# launchd wrapper — com.valleypawn.markdown-verification-review (native, 2026-10-05; replaces Cowork weekly-markdown-verification-review).
AGENT="weekly-markdown-verification-review"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 60
"$PY" "$BIN/markdown_verification.py" review "$@" >> "$VLOG/$AGENT.log" 2>&1
