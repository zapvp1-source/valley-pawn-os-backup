#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== contract lines present? ====="
python3 "$BIN/log_triage.py" --days 7
python3 "$BIN/agent_doctor.py"
echo "===== nightly doctor — must now DM, not say clean ====="
bash "$BIN/fleet_doctor.sh"
