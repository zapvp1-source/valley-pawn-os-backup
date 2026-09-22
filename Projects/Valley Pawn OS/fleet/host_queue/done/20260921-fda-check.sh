#!/bin/bash
# READ-ONLY: did the Full Disk Access grant land? Route 1 only answers if it did.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/storage_diag.sh" tmcheck
echo "===== unified-search: did last night's rebuild finally read Mail/Messages? ====="
python3 "$BIN/inspect_path.py" "$HOME/Documents/Claude/Projects/Unified Search/.refresh_attempt.log" --lines 40
python3 "$BIN/inspect_path.py" "$HOME/Documents/Claude/Projects/Unified Search/stats.txt" --lines 20
echo "===== disk health: is the 16-day false CRITICAL gone? ====="
python3 "$BIN/inspect_path.py" "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/.disk_health_state.json" --lines 20
