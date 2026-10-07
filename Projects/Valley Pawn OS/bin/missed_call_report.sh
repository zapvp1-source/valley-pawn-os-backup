#!/bin/bash
# launchd wrapper — com.valleypawn.missed-call-report, Mondays 08:07 (native, 2026-10-06; replaces Cowork missed-call-text-report).
AGENT="missed-call-text-report"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 60
"$PY" "$BIN/missed_call_report.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
