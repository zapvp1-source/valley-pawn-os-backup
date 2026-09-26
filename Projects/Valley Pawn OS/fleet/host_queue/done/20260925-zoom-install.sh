#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/install_agent.sh" com.valleypawn.zoom-missed-alert
bash "$BIN/install_agent.sh" com.valleypawn.zoom-missed-eod
python3 "$BIN/agent_doctor.py"
