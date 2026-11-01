#!/bin/bash
# launchd wrapper — com.valleypawn.conductwatch-report (daily 07:35). Built 2026-10-31.
# DMs Joshua the last business day's verified camera moments + clips (catches up to 3 days; duplicate-guarded).
# Usage: conduct_watch_report.sh [--render] [--date YYYY-MM-DD]
AGENT="conductwatch-report"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
[ $# -gt 0 ] || vp_live_gate "$AGENT"
vp_lock "$AGENT" 60
cd "$HOME/Documents/Claude/Projects/Store Conduct Watch" || exit 1
mkdir -p logs
"$HOME/.vp-studio/conduct-watch-venv/bin/python" report.py "$@" 2>&1 | tee -a "$VLOG/$AGENT.log" >> "logs/$AGENT.log"
RC=${PIPESTATUS[0]}
[ $RC -eq 0 ] || ledger "$AGENT" "Camera watch report did not post (rc=$RC)" "no"
exit $RC
