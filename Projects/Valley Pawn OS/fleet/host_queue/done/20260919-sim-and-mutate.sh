#!/bin/bash
# Full sandbox: the suite, then mutation testing to prove the suite has teeth.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== SUITE ====="
python3 "$BIN/fleet_sim.py"
echo "===== MUTATION ====="
python3 "$BIN/fleet_sim.py" --mutate
