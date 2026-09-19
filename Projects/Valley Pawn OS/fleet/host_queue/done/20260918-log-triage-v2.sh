#!/bin/bash
# Re-triage with schedule-aware staleness. Read-only.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/log_triage.py" --days 7
