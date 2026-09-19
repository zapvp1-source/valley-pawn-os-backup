#!/bin/bash
# Run the nightly doctor ONCE by hand to prove it works, then install it as a launchd agent.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== 1. one manual run (this DOES DM if it finds something — that is the point) ====="
bash "$BIN/fleet_doctor.sh"
echo "===== 2. install the 02:10 agent ====="
bash "$BIN/install_agent.sh" com.valleypawn.fleet-doctor
echo "===== 3. confirm the agent is healthy ====="
python3 "$BIN/agent_doctor.py"
