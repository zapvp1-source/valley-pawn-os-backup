#!/bin/bash
# HOST JOB — nics-weekly-mtd-ranking (2026-09-21): single-store retry for LEX only.
# Main MTD pull (nics-mtd-ranking-2026-09-21) succeeded for CUL/HAR/ROA/WAY; LEX errored
# ("Could not select 'Claude NICS Transfers' after 3 attempts" - a one-off UI select miss).
# Per task instructions, retry the missing store ONCE with a single-store trigger.
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"

echo "=== nics-transfers MTD single-store retry: LEX ==="
bash "$BIN/bravo_pull.sh" nics-transfers "2026-09-01..2026-09-21" LEX nics-mtd-ranking-2026-09-21-lex-retry
PULL_EXIT=$?
echo "pull exit=$PULL_EXIT"
exit $PULL_EXIT
