#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/skill_dump.py" zoom-voicemail-alert 9000
echo "=========== EAW"
python3 "$BIN/skill_dump.py" email-analytics-weekly 9000
echo "=========== NWRA"
python3 "$BIN/skill_dump.py" northwest-registered-agent-daily-check 7000
echo "=========== ZOOM EOD"
python3 "$BIN/skill_dump.py" zoom-voicemail-eod-review 5000
