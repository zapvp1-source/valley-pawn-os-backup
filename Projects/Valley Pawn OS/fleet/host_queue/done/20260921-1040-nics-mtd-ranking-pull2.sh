#!/bin/bash
# HOST JOB — nics-weekly-mtd-ranking (2026-09-21), retry 2. First attempt (20260921-1000) hit
# pipeline contention from a concurrent employee-perf-refresh job and never reached bravo_run.
# That job finished cleanly at 09:33:48 ET; Bravo should now be idle. Retry the MTD pull.
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"

echo "=== nics-transfers MTD pull retry (2026-09-01..2026-09-21, all 5 stores) ==="
bash "$BIN/bravo_pull.sh" nics-transfers "2026-09-01..2026-09-21" CUL,HAR,LEX,ROA,WAY nics-mtd-ranking-2026-09-21b
PULL_EXIT=$?
echo "pull exit=$PULL_EXIT"
exit $PULL_EXIT
