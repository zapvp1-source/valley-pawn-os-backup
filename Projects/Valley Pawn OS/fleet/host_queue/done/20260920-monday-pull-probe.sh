#!/bin/bash
# LIVE probe of ONE report name against the real pipeline. Sunday 01:00 — no store contention.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/monday_pull.sh" --only aged-inventory-summary
echo "===== what landed in output/ for this report today ====="
python3 "$BIN/inspect_path.py" "$HOME/Documents/Claude/Projects/Bravo Data Extraction/output" --lines 1
