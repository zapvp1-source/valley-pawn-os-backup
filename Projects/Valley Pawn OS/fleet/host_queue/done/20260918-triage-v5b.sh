#!/bin/bash
# Archive the retired collector's logs via the guarded tool, then re-triage.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== safety: refuse to archive logs of a LIVE agent ====="
bash "$BIN/retire_agent.sh" com.valleypawn.fleet-doctor --archive-logs
echo "===== archive the dead one ====="
bash "$BIN/retire_agent.sh" com.valleypawn.dashboarddatacollector --archive-logs
echo "===== triage v5 ====="
python3 "$BIN/log_triage.py" --days 7
