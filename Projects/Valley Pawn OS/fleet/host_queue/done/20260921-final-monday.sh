#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/usearch_scan_probe.py"
echo "===== FINAL MONDAY TALLY ====="
python3 "$BIN/recent_truth.py" --days 2
