#!/bin/bash
# Isolation test of the publish guard. Proves a real send is diverted, then proves the guard is OFF.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== 1. baseline: guard should be OFF ====="
python3 "$BIN/vp_dryrun.py" status
echo "===== 2. arm the guard for 5 minutes ====="
python3 "$BIN/vp_dryrun.py" on --minutes 5 --reason "isolation self-test 2026-09-18"
python3 "$BIN/vp_dryrun.py" status
echo "===== 3. attempt a REAL DM through vp_slack — must be diverted, not sent ====="
export VP_TASK=dryrun-selftest
python3 "$BIN/vp_slack.py" dm "If you are reading this in Slack, the publish guard FAILED."
echo "===== 4. disarm ====="
python3 "$BIN/vp_dryrun.py" off
python3 "$BIN/vp_dryrun.py" status
echo "===== 5. confirm NO real receipt was written for the diverted send ====="
python3 "$BIN/vp_receipt.py" last dryrun-selftest
