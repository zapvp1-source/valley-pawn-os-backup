#!/bin/bash
# launchd wrapper — native monthly-analytics-report (Mac-first wave 3, 2026-10-19). Dormant unless fleet/state/native_live/monthly-analytics-report exists (bin/vp_live.sh).
AGENT="monthly-analytics-report"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 150
# 2026-10-22 DST guard: 11/1/2026 01:45 falls in the repeated 1:00-2:00 hour (clocks go back at 2:00 EDT), so launchd
# can start this twice, an hour apart. The first run creates the Google Sheet BEFORE its posted-already check, so a
# second run would leave a duplicate sheet. Any run started less than 90 min after the last scheduled start exits.
if [ $# -eq 0 ]; then
  STAMP="$OS_DIR/fleet/state/monthly_analytics_last_start"; NOW=$(date +%s)
  if [ -f "$STAMP" ] && [ $((NOW - $(cat "$STAMP" 2>/dev/null || echo 0))) -lt 5400 ]; then vlog "started again within 90 min of the last run (DST repeat hour) — exit"; exit 0; fi
  echo "$NOW" > "$STAMP"
fi
"$PY" "$BIN/monthly_analytics_report.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
