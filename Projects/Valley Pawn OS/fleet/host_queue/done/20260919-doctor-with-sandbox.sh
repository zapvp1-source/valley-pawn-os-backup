#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/fleet_doctor.sh"
echo "===== report section 0 ====="
python3 "$BIN/inspect_path.py" "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/doctor/2026-09-19.md" --lines 16
