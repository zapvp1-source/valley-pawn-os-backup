#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== DRY ====="
python3 "$BIN/install_data_first_gate.py"
echo "===== APPLY ====="
python3 "$BIN/install_data_first_gate.py" --apply
echo "===== idempotency ====="
python3 "$BIN/install_data_first_gate.py"
echo "===== pull progress ====="
python3 "$BIN/inspect_path.py" "$HOME/Documents/Claude/Projects/Bravo Data Extraction/logs/_monday_pull_status_2026-09-20.txt" --lines 12
