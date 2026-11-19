#!/bin/bash
# launchd wrapper - native monthly gold-bucket creation (2026-11-18, Joshua 11/17). 15th 18:12 ET, retries 16th/17th
# (the .py exits at once if the month is already done). Dormant unless fleet/state/native_live/scrap-create-monthly exists.
AGENT="scrap-create-monthly"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
"$PY" "$BIN/scrap_create_monthly.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
