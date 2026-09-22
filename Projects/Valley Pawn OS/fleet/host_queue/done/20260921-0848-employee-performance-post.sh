#!/bin/bash
# HOST JOB — monday-bravo-postcheck: post #employee-performance now that MTD employee-activity
# CSVs were refreshed (see 20260921-0840-employee-performance-backfill.sh). Allow-listed scripts only.
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"

/usr/bin/python3 "$BIN/comms_engine.py" post --pub employee-performance --pipeline-date 2026-09-21 --post-date 2026-09-21
POST_EXIT=$?
echo "post exit=$POST_EXIT"
exit $POST_EXIT
