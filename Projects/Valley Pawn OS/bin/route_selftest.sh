#!/bin/bash
# route_selftest.sh — proves bin/vp_route.py inside vp_slack.py on the host (Keychain token), against the
# private #vp-ops-shadow channel only. Uses fleet/slack_routes.selftest.json, never the live table.
OS_DIR="$HOME/Documents/Claude/Projects/Valley Pawn OS"
export VP_ROUTES_FILE="$OS_DIR/fleet/slack_routes.selftest.json"
export VP_TASK="route-selftest"
CH=C0BLQSABGGY
echo "== 1 quiet (expect ROUTED quiet, no post)"
/usr/bin/python3 "$OS_DIR/bin/vp_slack.py" post $CH "ROUTE-SELFTEST quiet — all clear"
echo "== 2 thread first (expect parent + reply)"
/usr/bin/python3 "$OS_DIR/bin/vp_slack.py" post $CH "ROUTE-SELFTEST reply one"
echo "== 3 thread second (expect reply under same parent)"
/usr/bin/python3 "$OS_DIR/bin/vp_slack.py" post $CH "ROUTE-SELFTEST reply two"
echo "== 4 has() sees threaded reply (expect 0)"
/usr/bin/python3 "$OS_DIR/bin/vp_slack.py" has $CH "reply two" 1; echo "rc=$?"
echo "== 5 has() misses the quiet one (expect 1)"
/usr/bin/python3 "$OS_DIR/bin/vp_slack.py" has $CH "ROUTE-SELFTEST quiet" 1; echo "rc=$?"
echo "== state"; cat "$OS_DIR/fleet/state/route_threads.json"
echo "== ledger"; tail -3 "$OS_DIR/fleet/quiet_ledger/$(date +%F).md"
