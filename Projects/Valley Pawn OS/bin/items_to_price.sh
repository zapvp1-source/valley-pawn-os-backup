#!/bin/bash
# launchd wrapper — com.valleypawn.items-to-price (daily 08:00, native, 2026-10-05). Replaces Cowork `daily-items-to-price`.
AGENT="daily-items-to-price"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 200
"$PY" "$BIN/items_to_price.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
