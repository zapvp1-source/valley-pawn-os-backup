#!/bin/bash
# Recovery for the 10/3-10/4 outage: items that run quickly / without Bravo first, then Saturday's daily reports.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/funds_verification.py" 2026-10-03
bash "$BIN/daily_report.sh" pawn 2026-10-03
bash "$BIN/daily_report.sh" sold 2026-10-03
bash "$BIN/daily_report.sh" discount 2026-10-03
