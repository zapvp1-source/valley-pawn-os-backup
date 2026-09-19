#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== archive retired collector logs (plist-derived) ====="
bash "$BIN/retire_agent.sh" com.valleypawn.dashboarddatacollector --archive-logs
echo "===== triage v6: still-failing vs resolved ====="
python3 "$BIN/log_triage.py" --days 7
