#!/bin/bash
# Full five-report Monday pull, run NOW to prove every report name before the 16:30 scheduled run.
# Sunday, stores closed — the safest window there is for Bravo.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/monday_pull.sh"
echo "===== certificate ====="
python3 "$BIN/tail_any.sh" 2>/dev/null
