#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/vp_slack.py" last C03CGTN3KN1 6
python3 "$BIN/vp_slack.py" has C03CGTN3KN1 "Report Period: 2026-10-04 (month-to-date)" 20
python3 "$BIN/vp_slack.py" last C0B17894S2Y 3
python3 "$BIN/agent_log_tail.py" monday-pull 30
python3 "$BIN/agent_log_tail.py" monday-compile 30
