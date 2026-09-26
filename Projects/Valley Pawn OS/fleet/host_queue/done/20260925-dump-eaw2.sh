#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/skill_dump.py" email-analytics-weekly 40000
echo "=========== NWRA"
python3 "$BIN/skill_dump.py" northwest-registered-agent-daily-check 20000
