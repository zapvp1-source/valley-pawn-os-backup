#!/bin/bash
# HOST JOB — nics-weekly-mtd-ranking (2026-09-21). Control_your_Mac/osascript is confirmed
# permanently gone (CHANGELOG 2026-09-20), so this task cannot recover Bravo itself. Use the
# sanctioned host job queue path per the DATA-FIRST GATE OVERRIDE: pull MTD nics-transfers for
# all 5 stores via the allow-listed bravo_pull.sh primitive (health-gates Bravo itself).
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"

echo "=== nics-transfers MTD pull (2026-09-01..2026-09-21, all 5 stores) ==="
bash "$BIN/bravo_pull.sh" nics-transfers "2026-09-01..2026-09-21" CUL,HAR,LEX,ROA,WAY nics-mtd-ranking-2026-09-21
PULL_EXIT=$?
echo "pull exit=$PULL_EXIT"
exit $PULL_EXIT
