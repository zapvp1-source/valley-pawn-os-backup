#!/bin/bash
# v5: benign-line filtering. Also archive the retired collector's logs so a dead fault stops counting.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
ARCH="$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/_retired-oneshots"
mkdir -p "$ARCH"
mv "$HOME/Library/Logs/valleypawn/dashboard-data-collector.err.log" "$ARCH/dashboard-data-collector.err.log.retired"
mv "$HOME/Library/Logs/valleypawn/dashboard-data-collector.out.log" "$ARCH/dashboard-data-collector.out.log.retired"
echo "===== triage v5 ====="
python3 "$BIN/log_triage.py" --days 7
