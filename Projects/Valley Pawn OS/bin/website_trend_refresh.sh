#!/bin/bash
# launchd wrapper — native vp-website-trend-daily-refresh (2026-10-14, Google re-grant prep). Dormant unless
# fleet/state/native_live/vp-website-trend-daily-refresh exists. Regenerates the Cowork artifact page
# ~/Documents/Claude/Artifacts/vp-website-trend/index.html (+ Desktop + dashboard copies) from the GA4 Data API.
AGENT="vp-website-trend-daily-refresh"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 30
"$PY" "$BIN/website_trend_refresh.py" --live "$@" >> "$VLOG/$AGENT.log" 2>&1
