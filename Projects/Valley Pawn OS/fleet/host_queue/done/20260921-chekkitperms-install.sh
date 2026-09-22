#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/install_agent.sh" com.valleypawn.chekkitperms-oneshot
python3 "$BIN/agent_doctor.py"
