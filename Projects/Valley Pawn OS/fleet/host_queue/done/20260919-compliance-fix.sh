#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== suite + mutation ====="
python3 "$BIN/fleet_sim.py"
python3 "$BIN/fleet_sim.py" --mutate
echo "===== compliance brief, dry run (proves it no longer hits channel_not_found) ====="
python3 "$BIN/compliance_brief.py" --dry-run
