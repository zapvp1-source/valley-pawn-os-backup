#!/bin/bash
# Retire the dead hourly agent. Dry run first, then apply, then re-run the doctor to verify.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== DRY ====="
bash "$BIN/retire_agent.sh" com.valleypawn.dashboarddatacollector
echo "===== APPLY ====="
bash "$BIN/retire_agent.sh" com.valleypawn.dashboarddatacollector --apply
echo "===== safety check: refuse to retire a HEALTHY agent ====="
bash "$BIN/retire_agent.sh" com.valleypawn.morning-pull
echo "===== doctor re-run ====="
python3 "$BIN/agent_doctor.py"
