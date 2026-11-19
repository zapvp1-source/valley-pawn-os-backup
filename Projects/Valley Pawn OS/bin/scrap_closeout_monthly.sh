#!/bin/bash
# launchd wrapper - NATIVE monthly scrap-gold closeout (2026-11-18, Rule 21). Daily 11:05 / 13:05 / 15:05 ET; the .py
# does nothing before the 10th or once the month is CLOSED. Dormant unless fleet/state/native_live/scrap-closeout-monthly.
# One-shot test args: put them in fleet/state/scrap_closeout/ARGS (read once, then deleted).
AGENT="scrap-closeout-monthly"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 170
A="$OS_DIR/fleet/state/scrap_closeout/ARGS"; EXTRA=""
if [ -f "$A" ]; then EXTRA=$(cat "$A"); rm -f "$A"; fi
"$PY" "$BIN/scrap_closeout_monthly.py" $EXTRA >> "$VLOG/$AGENT.log" 2>&1
