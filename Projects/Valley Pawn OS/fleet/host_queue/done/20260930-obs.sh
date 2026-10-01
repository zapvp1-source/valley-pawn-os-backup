#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/grep_skill.py" daily-clockin-check "gusto.com"
python3 "$BIN/grep_skill.py" daily-clockin-check "list_time"
python3 "$BIN/grep_skill.py" gusto-keep-alive "why"
python3 "$BIN/grep_skill.py" monday-bravo-combined-compile "result.json"
python3 "$BIN/grep_skill.py" monday-bravo-combined-run "trigger"
python3 "$BIN/skill_dump.py" chekkit-culpeper-sms-ticket-watch 1500
python3 "$BIN/skill_dump.py" monday-bravo-cell-gapfill 1500
