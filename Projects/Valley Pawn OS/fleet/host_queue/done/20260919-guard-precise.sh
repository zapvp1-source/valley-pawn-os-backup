#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/fleet_sim.py"
echo "===== mutation ====="
python3 "$BIN/fleet_sim.py" --mutate
echo "===== compliance brief dry run ====="
python3 "$BIN/compliance_brief.py" --dry-run
