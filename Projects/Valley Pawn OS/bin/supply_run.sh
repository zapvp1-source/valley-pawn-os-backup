#!/bin/bash
# launchd wrapper — com.valleypawn.supply-run (native, 2026-10-21). See bin/supply_order.py.
AGENT="supply-order"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "supply-order" 120
"$PY" "$BIN/supply_order.py" run "$@" >> "$VLOG/supply-order.log" 2>&1
