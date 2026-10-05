#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/agent_log_tail.py" monday-pull 25
python3 "$BIN/agent_doctor.py"
