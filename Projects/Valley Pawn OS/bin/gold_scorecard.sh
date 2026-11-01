#!/bin/bash
# launchd wrapper — com.valleypawn.gold-scorecard (Mon 07:40, native, 2026-10-31). The weekly measure+evaluate
# step of Gold and Silver Markeitng/GOLD_PLAN_OPERATING_LOOP.md. No Bravo touch (reads intake-detail CSVs),
# GA4 + Search Console via the cached OAuth token, Chekkit via per-store Keychain tokens. Posts nothing.
AGENT="gold-scorecard"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 120
GS="$HOME/Documents/Claude/Projects/Gold and Silver Markeitng"
"$PY" "$GS/bin/gold_scorecard.py" "$@" >> "$VLOG/$AGENT.log" 2>&1; rc=$?
vlog "gold_scorecard rc=$rc latest=$(ls -t "$GS/ceo-briefing/gold"/report_2*.md 2>/dev/null | head -1)"
# mirror for cloud sessions (Drive connector) — same pattern as analytics_api_pull.sh
OUTD="$HOME/Library/CloudStorage/GoogleDrive-jdavis@fcfpawn.com/My Drive/Valley Pawn Data/analytics"
[ -d "$OUTD" ] && cp -f "$GS/ceo-briefing/gold/report_latest.md" "$OUTD/gold_scorecard_latest.md" 2>/dev/null && cp -f "$GS/ceo-briefing/gold/week_latest.json" "$OUTD/gold_scorecard_latest.json" 2>/dev/null
exit $rc
