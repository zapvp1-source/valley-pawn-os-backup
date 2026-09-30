#!/bin/bash
# HOST JOB — nics-weekly-mtd-ranking backfill for the missed 2026-09-28 run.
# 9/28 run: WAY + HAR pulled clean (files on disk for 09-01..09-28); CUL report-select failed 3x,
# LEX stuck, ROA never started -> nothing posted (all-or-nothing rule).
# Pattern proven 2026-09-21: single-store sequential pulls succeed where the combined pull fails.
# Queued by an interactive session 2026-09-29 at Joshua's direction ("fix what you can fix now").
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
RANGE="2026-09-01..2026-09-28"
FAIL=0
for S in CUL LEX ROA; do
  echo "=== nics-transfers MTD backfill: $S $RANGE ==="
  bash "$BIN/bravo_pull.sh" nics-transfers "$RANGE" "$S" "nics-mtd-backfill-20260929-$S"
  RC=$?
  if [ $RC -ne 0 ]; then
    echo "$S first attempt exit=$RC — retrying once after 90s"
    sleep 90
    bash "$BIN/bravo_pull.sh" nics-transfers "$RANGE" "$S" "nics-mtd-backfill-20260929-$S-r2"
    RC=$?
  fi
  echo "$S exit=$RC"
  [ $RC -ne 0 ] && FAIL=1
done
exit $FAIL
