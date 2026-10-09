#!/bin/bash
# launchd wrapper — native vp-website-shop-nightly (Mac-first wave 1, 2026-10-08). Dormant unless fleet/state/native_live/vp-website-shop-nightly exists.
AGENT="vp-website-shop-nightly"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 30
"$PY" "$HOME/Documents/Claude/Projects/Website/analytics/bin/shop_refresh.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
