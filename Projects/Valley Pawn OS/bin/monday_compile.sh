#!/bin/bash
# launchd wrapper — com.valleypawn.monday-compile, Mon 08:45. Native Monday ops posts (2026-09-30).
# Runs AFTER the Cowork monday-bravo-combined-compile (08:00) and postcheck (08:30): every post it makes is
# de-duplicated against the channel, so while both exist it only fills what the Cowork run missed; after
# the 10/6 cloud move it carries the Monday reports on its own. --render = print only.
AGENT="monday-bravo-combined-compile"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
[ "$1" = "--render" ] || vp_lock "monday-compile" 60
"$PY" "$BIN/monday_compile.py" "$@" 2>&1 | tee -a "$VLOG/monday-compile.log"
exit ${PIPESTATUS[0]}
