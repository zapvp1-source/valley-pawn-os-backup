#!/bin/bash
# launchd wrapper — com.valleypawn.spot-prices, daily 07:00 (native, 2026-10-05). Fetch + guard + write spot_prices.json,
# then push the same numbers to the website calculators (bin/spot_site_update.py).
AGENT="vp-weekly-spot-price-update"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 20
"$PY" "$OS_DIR/fetch_spot_prices.py" >> "$VLOG/$AGENT.log" 2>&1; rc=$?
echo "fetch rc=$rc" >> "$VLOG/$AGENT.log"
[ -f "$BIN/spot_site_update.py" ] && "$PY" "$BIN/spot_site_update.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
exit $rc
