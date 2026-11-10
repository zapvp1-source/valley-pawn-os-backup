#!/bin/bash
# launchd wrapper for continuity_selftest.py (weekly, Sun 03:10). Via ~/bin/vp-runner (TCC).
AGENT=continuity-selftest; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; vp_lock $AGENT 30
"$PY" "$BIN/continuity_selftest.py" "$@"
rc=$?; vlog "continuity selftest rc=$rc"; exit 0
