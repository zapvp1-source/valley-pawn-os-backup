#!/bin/bash
# launchd wrapper — com.valleypawn.email-test-loop (native, 2026-11-17). $1 = apply | grade
AGENT="email-test-loop"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 30
"$PY" "$BIN/email_test_loop.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
