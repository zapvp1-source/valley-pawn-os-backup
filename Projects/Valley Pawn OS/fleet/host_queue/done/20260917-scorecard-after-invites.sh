#!/bin/bash
# HOST JOB — re-score after the vp_ops_engine channel invites (allow-listed, one command per line).
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
/usr/bin/python3 "$BIN/field_scorecard.py"
