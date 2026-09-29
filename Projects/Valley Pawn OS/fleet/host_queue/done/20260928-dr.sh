#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/agent_log_tail.py" daily-report-pawn 15
python3 "$BIN/agent_log_tail.py" daily-report-sold 6
