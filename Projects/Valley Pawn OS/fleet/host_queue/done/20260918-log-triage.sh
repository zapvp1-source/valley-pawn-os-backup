#!/bin/bash
# Find native agents that are silently dead or crashing. Read-only.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/log_triage.py" --days 7
