#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
/usr/bin/python3 "$BIN/zoom_missed_alert.py" eod --render
/usr/bin/python3 "$BIN/zoom_missed_alert.py" alert --render
bash "$BIN/tail_any.sh" missed_call_text/run.log 25
