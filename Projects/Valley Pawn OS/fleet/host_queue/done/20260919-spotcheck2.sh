#!/bin/bash
# Are the "daily defects" real absences, or markers that stopped matching? Read-only.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/audit_spotcheck.py" daily-cloudcover-check --max 6
python3 "$BIN/audit_spotcheck.py" pawn-walk --max 6
python3 "$BIN/audit_spotcheck.py" daily-items-to-price --max 6
python3 "$BIN/audit_spotcheck.py" daily-dress-code-check --max 6
python3 "$BIN/audit_spotcheck.py" daily-funds-verification --max 5
python3 "$BIN/audit_spotcheck.py" chekkit-unanswered-eod-followup --max 5
