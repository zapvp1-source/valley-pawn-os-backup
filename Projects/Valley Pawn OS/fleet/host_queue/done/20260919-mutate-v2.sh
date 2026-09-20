#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== SUITE (must stay green) ====="
python3 "$BIN/fleet_sim.py"
echo "===== MUTATION (all must be CAUGHT) ====="
python3 "$BIN/fleet_sim.py" --mutate
