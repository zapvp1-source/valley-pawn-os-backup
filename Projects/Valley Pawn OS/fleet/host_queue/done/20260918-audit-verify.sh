#!/bin/bash
# Re-run the audit after the {PREV-YYYY-MM} fix + receipt conversions. Read-only, publishes NOTHING.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/vp_audit.py" --days 60
