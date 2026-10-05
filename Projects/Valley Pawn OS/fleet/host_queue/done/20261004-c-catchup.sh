#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/catchup.py" --render
bash "$BIN/install_agent.sh" com.valleypawn.catchup
