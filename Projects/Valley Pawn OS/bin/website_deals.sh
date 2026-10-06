#!/bin/bash
# launchd wrapper — com.valleypawn.website-deals (native, 2026-10-05).
AGENT="vp-website-deals-weekly"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 60
"$PY" "$BIN/website_deals.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
