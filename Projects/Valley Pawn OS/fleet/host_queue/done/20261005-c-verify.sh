#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/monday_compile.py" --render --post-date 2026-10-05
python3 "$BIN/vp_slack.py" has C03CGTN3KN1 "Report Period: 2026-10-04 (month-to-date)" 20
echo has_rc=$?
python3 "$BIN/comms_engine.py" check --pub first-payment-default --pipeline-date 2026-10-04 --post-date 2026-10-05
echo fpd_check_rc=$?
