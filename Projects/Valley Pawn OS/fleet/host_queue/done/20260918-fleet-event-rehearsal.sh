#!/bin/bash
# Prove the fleet-event alarm fires BEFORE an outage happens. Simulation: DMs nothing,
# marks its ledger row SIMULATED, and resets its own state so a real event still alerts as day 1.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== normal run first (no simulation) ====="
python3 "$BIN/field_scorecard.py" --dry
echo "===== now the rehearsal ====="
python3 "$BIN/field_scorecard.py" --simulate-fleet-event
echo "===== ledger tail ====="
python3 "$BIN/tail_any.sh" 2>/dev/null
