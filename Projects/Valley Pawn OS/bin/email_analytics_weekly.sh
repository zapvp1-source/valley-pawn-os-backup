#!/bin/bash
# launchd wrapper for bin/email_analytics_weekly.py — com.valleypawn.email-analytics-weekly, Fri 03:30.
# Native replacement for the Cowork task email-analytics-weekly (2026-09-25). --render = no writes.
AGENT="email-analytics-weekly"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
RENDER=0; for a in "$@"; do [ "$a" = "--render" ] && RENDER=1; done
[ $RENDER -eq 0 ] && vp_lock "$AGENT" 30
"$PY" "$BIN/email_analytics_weekly.py" "$@" 2>&1 | grep -vE 'FutureWarning|warnings.warn|NotOpenSSLWarning|^\s*$' | tee -a "$VLOG/$AGENT.log"
exit ${PIPESTATUS[0]}
