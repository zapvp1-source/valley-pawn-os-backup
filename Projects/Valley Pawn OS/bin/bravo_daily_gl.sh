#!/bin/bash
# launchd wrapper — com.valleypawn.bravo-daily-gl (00:45 + 03:15 catch-up), daily Bravo -> QuickBooks posting (Joshua 2026-10-21). Live by design.
AGENT="bravo-daily-gl"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 230
"$PY" "$BIN/bravo_daily_gl.py" "$@" >> "$OS_DIR/fleet/state/bravo_daily_gl/run.log" 2>&1
"$PY" "$BIN/qbo_depreciation.py" >> "$OS_DIR/fleet/state/bravo_daily_gl/run.log" 2>&1
