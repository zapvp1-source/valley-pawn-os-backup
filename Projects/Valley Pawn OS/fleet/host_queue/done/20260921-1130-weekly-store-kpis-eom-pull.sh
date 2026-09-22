#!/bin/bash
# HOST JOB — weekly-store-kpis (2026-09-21): 5-store end-of-month MTD pull for the Weekly Store
# KPIs scorecard. Needed because no 2026-09-20 end-of-month xlsx exists on disk yet for any store
# (data-first gate check found only 09-05..09-10 files). Range FIRST..YESTERDAY per task steps.
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "=== weekly-store-kpis end-of-month MTD pull, all 5 stores ==="
bash "$BIN/bravo_pull.sh" end-of-month "2026-09-01..2026-09-20" CUL,HAR,LEX,ROA,WAY wskpi-2026-09-21-eom
PULL_EXIT=$?
echo "pull exit=$PULL_EXIT"
exit $PULL_EXIT
