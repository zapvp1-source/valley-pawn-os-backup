#!/bin/bash
# HOST JOB — monday-bravo-postcheck backfill for #employee-performance (2026-09-21).
# The MTD employee-activity CSVs (first-of-month keyed) are stale (last pulled 9/6), so the
# employee-performance publication would withhold. Refresh the MTD pull for all 5 stores, then
# render+post via the comms engine (VP OPS ENGINE bot). Allow-listed scripts only.
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"

echo "=== step 1: refresh MTD employee-activity pull (2026-09-01 .. today) ==="
bash "$BIN/bravo_pull.sh" employee-activity 2026-09-01 CUL,HAR,LEX,ROA,WAY employee-mtd-refresh-2026-09-21
PULL_EXIT=$?
echo "pull exit=$PULL_EXIT"

echo "=== step 2: post employee-performance via comms engine ==="
/usr/bin/python3 "$BIN/comms_engine.py" post --pub employee-performance --pipeline-date 2026-09-20 --post-date 2026-09-21
POST_EXIT=$?
echo "post exit=$POST_EXIT"

exit $POST_EXIT
