#!/bin/bash
# Gate v2 — with correlated-outage detection and the RETIRE-vs-late fix. Read-only.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
OUT="$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/audit.json"
python3 "$BIN/vp_audit.py" --days 60 --json "$OUT"
echo "=================== GATE v2 ==================="
python3 "$BIN/fleet_gate.py" --json "$OUT"
