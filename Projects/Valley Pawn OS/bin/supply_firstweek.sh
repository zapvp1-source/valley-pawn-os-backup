#!/bin/bash
# launchd wrapper — com.valleypawn.supply-firstweek, ONE-TIME Tue 2026-10-27 11:00 check Joshua asked for (native, 2026-10-22).
AGENT="supply-order"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "supply-order" 120
"$PY" "$BIN/supply_order.py" firstweek "$@" >> "$VLOG/supply-order.log" 2>&1
