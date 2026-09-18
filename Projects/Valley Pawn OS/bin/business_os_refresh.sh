#!/bin/bash
# Native replacement for business-os-daily-refresh — 2026-09-17. The script itself rewrites the LIVE STATE block + CHANGELOG line.
AGENT=business-os-refresh; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; vp_lock $AGENT 30
$PY "$OS_DIR/bin/refresh_live_state.py" > "$VLOG/business-os-refresh.out" 2>&1; rc=$?
vlog "refresh_live_state.py rc=$rc :: $(tail -2 "$VLOG/business-os-refresh.out" | tr '\n' ' ' | cut -c1-200)"
[ $rc -eq 0 ] || ledger "business-os-daily-refresh" "The daily BUSINESS_OS live-state refresh did not complete (exit $rc)." "no"
exit $rc
