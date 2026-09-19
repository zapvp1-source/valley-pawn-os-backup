#!/bin/bash
# Verify the watchdog runs again after the corrupt-state fix, then rehearse the fleet-event alarm.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== 1. normal run (dry) — must NOT crash ====="
python3 "$BIN/field_scorecard.py" --dry
echo "===== 2. fleet-event rehearsal — DMs nothing, ledger row marked SIMULATED ====="
python3 "$BIN/field_scorecard.py" --simulate-fleet-event
