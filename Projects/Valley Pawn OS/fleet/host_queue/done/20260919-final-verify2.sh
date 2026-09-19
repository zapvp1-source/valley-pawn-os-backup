#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== triage v8 (must not crash) ====="
python3 "$BIN/log_triage.py" --days 7
echo "===== nightly doctor, full run ====="
bash "$BIN/fleet_doctor.sh"
echo "===== doctor report header ====="
python3 "$BIN/inspect_path.py" "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/doctor/2026-09-19.md" --lines 12
