#!/bin/bash
# READ-ONLY: confirm the new SSD is factory-empty before anyone proposes reformatting it.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/inspect_path.py" "/Volumes/SB-XTM5" --lines 5
echo "===== what is actually eating the internal disk ====="
bash "$BIN/storage_diag.sh" big
