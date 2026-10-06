#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
cd "$BIN"
/usr/bin/python3 zoom_missed_alert.py eod --render
echo "--- alert render ---"
/usr/bin/python3 zoom_missed_alert.py alert --render
echo "--- log tail ---"
bash "$BIN/tail_any.sh" missed_call_text/run.log 30 | grep -i -E "chekkit|handled"
