#!/bin/bash
# launchd wrapper — com.valleypawn.spot-prices (native, 2026-10-05).
AGENT="vp-weekly-spot-price-update"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 60
"$PY" "$BIN/spot_prices_unused.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
