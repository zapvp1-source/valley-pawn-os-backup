#!/bin/bash
# HOST JOB — Phase 0.4/0.5: reload the scorecard agent after adding the fresh-miss window
# (no DMs/notices for misses older than 30h) and the Phase 0.5 delayed-notice line.
set +e
U=$(id -u)
OS="$HOME/Documents/Claude/Projects/Valley Pawn OS"
echo "=== rerun3 start $(date) ==="
/usr/bin/python3 "$OS/bin/field_scorecard.py" 2>&1; echo "rc=$?"
launchctl kickstart -k gui/$U/com.valleypawn.field-scorecard 2>&1 && echo "agent restarted"
sleep 2; launchctl list | grep field-scorecard
tail -6 "$HOME/Library/Logs/valleypawn/field-scorecard.log"
echo "=== rerun3 done $(date) ==="
