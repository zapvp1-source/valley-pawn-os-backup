#!/bin/bash
# launchd wrapper — native mobilepawn-app-social-monthly (Mac-first wave 3, 2026-10-19). 20th of month 09:10 ET.
# Dormant unless fleet/state/native_live/mobilepawn-app-social-monthly exists (bin/vp_live.sh).
# SKILL: run MobilePawn Participation/app_outreach/monthly_post.py (next month, idempotent via sent_log.json,
# schedules through vp_social_publisher.py for the 2nd Tuesday 11:00 ET and verifies every Publer job).
# Fails -> re-run once -> one FAILURE_LEDGER row + ONE plain DM to Joshua (the SKILL's wording). Success = silent.
#   --render  = monthly_post.py --dry-run (no Publer writes)
AGENT="mobilepawn-app-social-monthly"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
APP="$HOME/Documents/Claude/Projects/MobilePawn Participation/app_outreach"
if [ "$1" = "--render" ]; then shift; cd "$APP" && "$PY" monthly_post.py --dry-run "$@"; exit $?; fi
vp_live_gate "$AGENT"
vp_lock "$AGENT" 60
cd "$APP" || exit 1
OUT=$("$PY" monthly_post.py 2>&1); RC=$?
if [ $RC -ne 0 ]; then vlog "first try failed (rc=$RC): $(echo "$OUT" | tail -3 | tr '\n' ' ')"; sleep 120; OUT=$("$PY" monthly_post.py 2>&1); RC=$?; fi
vlog "rc=$RC $(echo "$OUT" | tail -2 | tr '\n' ' ')"
if [ $RC -ne 0 ]; then
  ledger "$AGENT" "Next month's MobilePawn app post did not get scheduled after two tries." "no"
  slack dm "Next month's MobilePawn app post didn't get scheduled — I'll retry." >/dev/null 2>&1
  exit 1
fi
exit 0
