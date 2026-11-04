#!/bin/bash
# launchd wrapper — com.valleypawn.storetraffic-nightly (Mon–Sat 21:35 ET). Door-counter self-check:
# coverage, IN/OUT balance, tickets/visitor, auto-exclusion of degraded days, retention. Code: Store Traffic Counter/health.py
# A DEGRADED store-day -> ONE Failure Ledger row (fleet-guardian surfaces it). Never Slack.
AGENT="storetraffic-nightly"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"; vp_lock "$AGENT" 60
export VPST_DIR="$HOME/.vp_secrets/store_traffic"
cd "$HOME/Documents/Claude/Projects/Store Traffic Counter" || exit 1
OUT=$("$HOME/.vp-studio/store-traffic-venv/bin/python" health.py 2>&1); RC=$?
vlog "$OUT"
if [ $RC -eq 2 ]; then ledger "storetraffic-nightly" "Door counter check: $(echo "$OUT" | grep '^DEGRADED' | cut -c11-300). Those store-days are left out of traffic reports automatically; counters self-restart." "no"
elif [ $RC -ne 0 ]; then ledger "storetraffic-nightly" "Door counter nightly check did not run (health.py exit $RC)." "no"; fi
exit 0
