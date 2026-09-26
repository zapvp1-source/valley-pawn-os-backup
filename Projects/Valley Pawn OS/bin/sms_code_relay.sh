#!/bin/bash
# launchd wrapper for bin/sms_code_relay.py — com.valleypawn.sms-code-relay, every 30 s.
AGENT="sms-code-relay"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
"$PY" "$BIN/sms_code_relay.py" "$@" 2>>"$VLOG/$AGENT.err.log"
