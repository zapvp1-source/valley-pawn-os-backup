#!/bin/bash
# Triage v3: schedule-aware staleness, and .err.log no longer treated as stale. Read-only.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/log_triage.py" --days 7
