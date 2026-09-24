#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/agent_log_tail.py" oura-daily-import 15
python3 "$BIN/agent_log_tail.py" backup-health-watchdog 5
