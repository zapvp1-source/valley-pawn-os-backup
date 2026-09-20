#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/audit_spotcheck.py" daily-dress-code-check --max 6
python3 "$BIN/audit_spotcheck.py" daily-clockin-check --max 5
python3 "$BIN/audit_spotcheck.py" discount-review --max 5
python3 "$BIN/audit_spotcheck.py" chekkit-unanswered-alert --max 5
