#!/bin/bash
# launchd wrapper — com.valleypawn.gold-silver-monthly (native, 2026-10-05).
AGENT="monthly-we-buy-gold-silver-email"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 60
"$PY" "$BIN/gold_silver_monthly.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
