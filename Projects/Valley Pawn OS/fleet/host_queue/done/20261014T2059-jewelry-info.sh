#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/skill_dump.py" jewelry-onhand-nightly-pull 40000
echo "=====CATCHUP====="
python3 "$BIN/skill_dump.py" jewelry-onhand-catchup 40000
echo "=====LAST====="
python3 "$BIN/vp_slack.py" last C0BM9NHGTT4 8
