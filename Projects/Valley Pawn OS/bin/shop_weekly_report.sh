#!/bin/bash
# launchd wrapper — native vp-website-shop-weekly-report (2026-10-14, Google re-grant prep). Dormant unless fleet/state/native_live/vp-website-shop-weekly-report exists.
AGENT="vp-website-shop-weekly-report"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 30
"$PY" "$BIN/shop_weekly_report.py" --send "$@" >> "$VLOG/$AGENT.log" 2>&1
