#!/bin/bash
# launchd wrapper — com.valleypawn.seasonal-campaigns (native, 2026-11-21). Daily 06:20. Read-only check; see seasonal_campaigns.py.
AGENT="seasonal-campaigns"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 30
"$PY" "$BIN/seasonal_campaigns.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
