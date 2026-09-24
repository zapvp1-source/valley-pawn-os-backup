#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/tail_log.py" oura-daily-import 15
python3 "$BIN/tail_log.py" backup-health-watchdog 5
