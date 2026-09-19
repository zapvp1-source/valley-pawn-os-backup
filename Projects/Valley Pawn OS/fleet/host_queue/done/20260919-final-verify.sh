#!/bin/bash
# Final verification pass: triage v8, then the full nightly doctor exactly as it will run at 02:10.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== triage v8 ====="
python3 "$BIN/log_triage.py" --days 7
echo "===== nightly doctor, full run ====="
bash "$BIN/fleet_doctor.sh"
echo "===== agents healthy? ====="
python3 "$BIN/agent_doctor.py"
