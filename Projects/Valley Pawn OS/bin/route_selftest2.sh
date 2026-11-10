#!/bin/bash
# route_selftest2.sh — headline + canvas path on the host, #vp-ops-shadow only.
OS_DIR="$HOME/Documents/Claude/Projects/Valley Pawn OS"
export VP_ROUTES_FILE="$OS_DIR/fleet/slack_routes.selftest.json"
export VP_TASK="route-selftest"
CH=C0BLQSABGGY
F=/tmp/route_selftest_body.txt
printf '*ROUTE-SELFTEST headline — Weekly Widget Review*\nCompany total: $12,345 (3 stores need a look)\n\n| Store | Count | Total |\n| --- | --- | --- |\n| Culpeper | 12 | $4,000 |\n| Roanoke | 9 | $3,345 |\n| Waynesboro | 15 | $5,000 |\n\nFull details in the spreadsheet.\n' > $F
echo "== 1 headline (expect short post + canvas section)"
/usr/bin/python3 "$OS_DIR/bin/vp_slack.py" post $CH --file $F
echo "== 2 thread+canvas (expect parent, short reply, canvas section)"
printf 'ROUTE-SELFTEST threadcanvas — Daily thing\nline two\n• a\n• b\n• c\n• d\n' > $F
/usr/bin/python3 "$OS_DIR/bin/vp_slack.py" post $CH --file $F
echo "== canvas state"; /usr/bin/python3 "$OS_DIR/bin/vp_canvas_section.py" status | grep -A3 selftest
echo "== last 2 messages"; /usr/bin/python3 "$OS_DIR/bin/vp_slack.py" last $CH 3
