#!/bin/bash
# launchd wrapper — com.valleypawn.markdown-verification-pull (native, 2026-10-05; replaces Cowork weekly-markdown-verification-pull).
AGENT="weekly-markdown-verification-pull"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 60
"$PY" "$BIN/markdown_verification.py" pull "$@" >> "$VLOG/$AGENT.log" 2>&1
