#!/bin/bash
# launchd wrapper — com.valleypawn.loan-layaway-dms (Mon 09:00). Native replacement for the Cowork task
# weekly-loan-layaway-manager-dms (2026-09-28). --render = print, send nothing.
AGENT="weekly-loan-layaway-manager-dms"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
RENDER=0; for a in "$@"; do [ "$a" = "--render" ] && RENDER=1; done
[ $RENDER -eq 0 ] && vp_lock "$AGENT" 20
"$PY" "$BIN/loan_layaway_dms.py" "$@" 2>&1 | tee -a "$VLOG/$AGENT.log"
exit ${PIPESTATUS[0]}
