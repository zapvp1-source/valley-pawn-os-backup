#!/bin/bash
# Triage v4: problems bounded to the window. Then a full nightly-doctor dry pass.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/log_triage.py" --days 2
echo "===== 7-day view ====="
python3 "$BIN/log_triage.py" --days 7
