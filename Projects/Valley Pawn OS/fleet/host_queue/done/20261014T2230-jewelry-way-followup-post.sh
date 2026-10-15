#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
VP_TASK=jewelry-onhand-nightly-pull
python3 "$BIN/vp_slack.py" post C0BM9NHGTT4 --file "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/state/jewelry_nightly/followup-2026-10-14-WAY-post.txt"
