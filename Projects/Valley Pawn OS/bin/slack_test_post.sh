#!/bin/bash
# slack_test_post.sh <file> — post a file to the private #vp-ops-shadow test channel only (formatting tests).
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
VP_TASK="formatting-test" "$PY" "$BIN/vp_slack.py" post C0BLQSABGGY --file "$1"
