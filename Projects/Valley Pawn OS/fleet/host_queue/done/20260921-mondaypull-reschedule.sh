#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== reinstall with Sunday 16:30 + Monday 05:30 ====="
bash "$BIN/install_agent.sh" com.valleypawn.monday-pull
echo "===== pull NOW so today's tasks have Monday-dated data ====="
bash "$BIN/monday_pull.sh"
