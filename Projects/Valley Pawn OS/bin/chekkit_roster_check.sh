#!/bin/bash
# launchd wrapper — com.valleypawn.chekkit-roster-check, 3rd of month 10:10 (beside the Bravo logins check at 10:00).
# Gusto roster vs Chekkit users per store; DMs Joshua once a month only when someone needs adding or removing.
AGENT="chekkit-roster-check"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
if [ "$1" = "--render" ]; then shift; "$PY" "$BIN/chekkit_roster_check.py" "$@"; exit $?; fi
vp_lock "$AGENT" 20
LINE=$("$PY" "$BIN/chekkit_roster_check.py" --send "$@" 2>>"$VLOG/$AGENT.log") || { vlog "script failed: $LINE"; exit 1; }
vlog "$LINE"
