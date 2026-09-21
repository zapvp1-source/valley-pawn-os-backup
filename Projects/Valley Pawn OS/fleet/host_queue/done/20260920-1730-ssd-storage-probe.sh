#!/bin/bash
# READ-ONLY probe: is the Thunderbolt SSD attached, and what is the real storage picture?
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== /Volumes (external drives mount here) ====="
python3 "$BIN/inspect_path.py" "/Volumes" --lines 1
echo "===== launchd agents ====="
bash "$BIN/host_diag.sh" agents
