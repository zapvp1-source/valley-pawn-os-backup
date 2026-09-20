#!/bin/bash
# Are the "daily defects" real absences, or markers that stopped matching? Read-only.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
for t in daily-cloudcover-check pawn-walk daily-items-to-price daily-dress-code-check; do
  python3 "$BIN/audit_spotcheck.py" "$t" --max 6
  echo
done
