#!/bin/bash
# monthly_prestage.sh — native replacement for Cowork `monthly-analytics-prestage` (days 28-31 20:00).
# The SKILL was already only a launcher: if tomorrow is the 1st and the runner is not running, start
# bin/monthly_prestage_runner.py and log one line to monthly-analytics/logs/launcher.out.
AGENT="monthly-analytics-prestage"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
[ "$(date -v+1d +%d)" = "01" ] || { [ "$1" = "--render" ] && echo "=== RENDER: tomorrow is not the 1st — would SKIP ==="; exit 0; }
[ "$1" = "--render" ] && { echo "=== RENDER: would launch monthly_prestage_runner.py ==="; exit 0; }
L="$OS_DIR/monthly-analytics/logs/launcher.out"; mkdir -p "$(dirname "$L")"
if pgrep -f monthly_prestage_runner.py >/dev/null; then echo "$(date '+%F %T') launcher: runner already running for $(date +%Y-%m) (native)" >> "$L"; exit 0; fi
( cd "$BIN" && $PY monthly_prestage_runner.py >> "$L" 2>&1 )    # foreground: launchd keeps it alive
RC=$?; echo "$(date '+%F %T') launcher: runner finished rc=$RC for $(date +%Y-%m) (native)" >> "$L"
[ $RC -eq 0 ] && $PY "$BIN/vp_receipt.py" write "$AGENT" --surface file --target "$L" >/dev/null 2>&1 || ledger "$AGENT" "The month-end analytics prestage did not finish cleanly." "no"
