#!/bin/bash
# READ-ONLY: full storage picture now that the Thunderbolt SSD is attached (/Volumes/SB-XTM5).
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/storage_diag.sh" volumes
bash "$BIN/storage_diag.sh" space
bash "$BIN/storage_diag.sh" tm
