#!/bin/bash
# Diagnose the two dead agents + the worst daily defect. Read-only.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "########## cloudcover task SKILL ##########"
python3 "$BIN/inspect_path.py" "$HOME/Documents/Claude/Scheduled/daily-cloudcover-check/SKILL.md" --lines 45
echo "########## jewelry-onhand-nightly-pull ##########"
python3 "$BIN/inspect_path.py" "$HOME/Documents/Claude/Scheduled/jewelry-onhand-nightly-pull/SKILL.md" --lines 30
