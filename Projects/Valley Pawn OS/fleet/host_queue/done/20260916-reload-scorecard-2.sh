#!/bin/bash
# HOST JOB — reload field-scorecard after the history-ledger strictness fix (UNVERIFIED != clean).
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
/usr/bin/python3 "$BIN/field_scorecard.py"
bash "$BIN/install_agent.sh" com.valleypawn.field-scorecard --restart-only
