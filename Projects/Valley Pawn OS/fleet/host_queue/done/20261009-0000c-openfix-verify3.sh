#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "=== log_triage ==="
python3 "$BIN/log_triage.py" --days 7
echo "=== fleet_sim ==="
python3 "$BIN/fleet_sim.py"
