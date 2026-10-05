#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/host_diag.sh" agents
python3 "$BIN/agent_log_tail.py" daily-funds-verification 15
python3 "$BIN/agent_log_tail.py" host-queue 25
python3 "$BIN/agent_log_tail.py" catchup 10
python3 "$BIN/agent_log_tail.py" daily-report-pawn 8
