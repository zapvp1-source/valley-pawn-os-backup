#!/bin/bash
# Score every Tier-1 publication against the go/no-go gate. Read-only, publishes NOTHING.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
OUT="$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/audit.json"
python3 "$BIN/vp_dryrun.py" status
python3 "$BIN/vp_audit.py" --days 60 --json "$OUT"
echo "=================== GATE ==================="
python3 "$BIN/fleet_gate.py" --json "$OUT"
