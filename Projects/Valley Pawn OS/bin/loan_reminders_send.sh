#!/bin/bash
# launchd wrapper - com.valleypawn.loan-reminders-send, 9:15 AM daily (2026-11-21). Sends ONLY for stores with a
# LIVE file (fleet/state/loan_reminders_live/<STORE>); with none it just logs what it would have sent.
AGENT="loan-reminders-send"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 40
"$PY" "$BIN/loan_reminders_send.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
