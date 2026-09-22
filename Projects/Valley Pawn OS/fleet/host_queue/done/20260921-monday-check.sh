#!/bin/bash
# MONDAY: did the weekly chain publish this time? Read with the posting app's own token.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== data on disk for today's reports ====="
python3 "$BIN/inspect_path.py" "$HOME/Documents/Claude/Projects/Bravo Data Extraction/logs/_monday_pull_status_2026-09-20.txt" --lines 10
echo "===== last 7 days, weekly tier ====="
python3 "$BIN/recent_truth.py" --days 7
