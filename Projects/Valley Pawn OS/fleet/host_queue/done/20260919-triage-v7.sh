#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== triage v7 ====="
python3 "$BIN/log_triage.py" --days 7
echo "===== scorecard sanity: must run clean twice in a row ====="
python3 "$BIN/field_scorecard.py" --dry-run
python3 "$BIN/field_scorecard.py" --dry-run
python3 "$BIN/state_shape.py"
