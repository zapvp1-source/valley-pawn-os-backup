#!/bin/bash
# Isolation test of the publish guard. A REAL DM is attempted; it must be diverted, never sent.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== 1. baseline: guard OFF ====="
python3 "$BIN/vp_dryrun.py" status
echo "===== 2. arm for 5 minutes ====="
python3 "$BIN/vp_dryrun.py" on --minutes 5 --reason "isolation self-test 2026-09-18"
echo "===== 3. attempt a REAL DM to Joshua — must divert ====="
python3 "$BIN/vp_slack.py" dm "If this appears in Slack, the publish guard FAILED."
echo "===== 4. audit must show the DRY RUN banner ====="
python3 "$BIN/vp_audit.py" --days 7
echo "===== 5. disarm and confirm ====="
python3 "$BIN/vp_dryrun.py" off
python3 "$BIN/vp_dryrun.py" status
echo "===== 6. a REAL send must work again (posts to Joshua DM — this one is intentional) ====="
python3 "$BIN/vp_slack.py" dm "Publish guard verified: diverted while armed, live again after. No action needed."
