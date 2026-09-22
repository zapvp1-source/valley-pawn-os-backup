#!/bin/bash
# HOST JOB — nics-weekly-mtd-ranking (2026-09-21): LEX single-store retry, attempt 2.
# Prior LEX-only retry (1052) hit "pipeline busy" for all 3 checks and exited without firing a
# trigger (likely still-finishing nics-mtd-ranking-2026-09-21b, which closed out at 10:08:51).
# Pipeline should be idle now. LEX has failed twice on report-select ("Claude NICS Transfers"
# not selectable after 3 attempts) - this is the last scripted retry per task instructions.
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"

echo "=== nics-transfers MTD single-store retry #2: LEX ==="
bash "$BIN/bravo_pull.sh" nics-transfers "2026-09-01..2026-09-21" LEX nics-mtd-ranking-2026-09-21-lex-retry2
PULL_EXIT=$?
echo "pull exit=$PULL_EXIT"
exit $PULL_EXIT
