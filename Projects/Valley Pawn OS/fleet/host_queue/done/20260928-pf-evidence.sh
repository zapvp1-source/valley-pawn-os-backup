#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/task_preflight.py" --task daily-items-to-price
python3 "$BIN/task_preflight.py" --task daily-cloudcover-check
python3 "$BIN/task_preflight.py" --task weekly-store-kpis
python3 "$BIN/task_preflight.py" --task monthly-analytics-report
python3 "$BIN/task_preflight.py" --task google-reviews-post-watchdog
