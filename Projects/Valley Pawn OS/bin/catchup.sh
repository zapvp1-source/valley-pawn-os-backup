#!/bin/bash
# launchd wrapper — com.valleypawn.catchup (RunAtLoad + every 15 min). See bin/catchup.py.
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
"$PY" "$BIN/catchup.py" "$@"
