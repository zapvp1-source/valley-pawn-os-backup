#!/bin/bash
# Publisher-only spot-check: real absence vs marker drift. Read-only.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/audit_spotcheck.py" daily-cloudcover-check --max 6
python3 "$BIN/audit_spotcheck.py" daily-dress-code-check --max 6
python3 "$BIN/audit_spotcheck.py" pawn-walk --max 4
python3 "$BIN/audit_spotcheck.py" daily-clockin-check --max 5
python3 "$BIN/audit_spotcheck.py" jewelry-onhand-nightly-pull --max 5
