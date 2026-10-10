#!/bin/bash
# launchd/host-queue wrapper — com.valleypawn.ceo-week-pull (native, 2026-10-09). Revenue data for the Weekly CEO Brief.
AGENT="ceo-week-pull"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 150
"$PY" "$BIN/ceo_week_pull.py" "$@" 2>&1 | tee -a "$VLOG/$AGENT.log"
rc=${PIPESTATUS[0]}
[ "$rc" = 0 ] || [ "$rc" = 3 ] || ledger "$AGENT" "Weekly CEO brief revenue pull did not finish; the brief will retry it before sending." "no"
exit $rc
