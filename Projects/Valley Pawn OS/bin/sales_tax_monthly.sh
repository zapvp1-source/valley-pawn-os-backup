#!/bin/bash
# launchd wrapper — native sales-tax-monthly-update (Mac-first wave 3, 2026-10-19). Dormant unless fleet/state/native_live/sales-tax-monthly-update exists (bin/vp_live.sh).
AGENT="sales-tax-monthly-update"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 170
"$PY" "$BIN/sales_tax_monthly.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
