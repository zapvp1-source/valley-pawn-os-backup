#!/bin/bash
# Render-test the Monday pull (no Bravo contact), then install it for 16:30 Sunday.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== render (touches nothing) ====="
bash "$BIN/monday_pull.sh" --render
echo "===== install the Sunday 16:30 agent ====="
bash "$BIN/install_agent.sh" com.valleypawn.monday-pull
echo "===== confirm healthy ====="
python3 "$BIN/agent_doctor.py"
