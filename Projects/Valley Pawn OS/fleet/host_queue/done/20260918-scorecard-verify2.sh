#!/bin/bash
# Verify the shadowing fix: no crash, and the state file holds a DICT afterwards.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== 1. dry run — must complete with no CRASH ====="
python3 "$BIN/field_scorecard.py" --dry-run
echo "===== 2. fleet-event rehearsal (DMs nothing) ====="
python3 "$BIN/field_scorecard.py" --simulate-fleet-event
echo "===== 3. state file must now be a dict, not a string ====="
python3 "$BIN/state_shape.py"
