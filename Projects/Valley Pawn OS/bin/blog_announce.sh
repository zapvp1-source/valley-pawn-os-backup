#!/bin/bash
# launchd wrapper — com.valleypawn.blog-announce (native, 2026-10-05).
AGENT="blog-announce"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 60
"$PY" "$BIN/blog_announce.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
