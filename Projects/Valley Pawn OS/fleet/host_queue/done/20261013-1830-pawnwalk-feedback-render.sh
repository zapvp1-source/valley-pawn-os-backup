# Pawn-walk feedback loop (2026-10-13): compile the 10/12 walk with the new feedback hook on the host,
# live Slack ingest, publish NOTHING (--render). Output lands in fleet/test_output/pawn-walk-2026-10-12.txt
OS_BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
/bin/bash "$OS_BIN/daily_report.sh" pawn 2026-10-12 --render
