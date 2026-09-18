#!/bin/bash
# HOST JOB — first job under the Phase 0.6 allow-list: one plain command per line, bin/ scripts only.
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "=== reload scorecard under allow-list ==="
/usr/bin/python3 "$BIN/changelog_recent.py"
bash "$BIN/install_agent.sh" com.valleypawn.field-scorecard --restart-only
bash "$BIN/host_diag.sh" scorecard agents
