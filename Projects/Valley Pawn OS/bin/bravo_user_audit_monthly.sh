#!/bin/bash
# launchd wrapper — native monthly-bravo-user-audit (Mac-first wave 3, 2026-10-19). 3rd of month 10:00 ET.
# Dormant unless fleet/state/native_live/monthly-bravo-user-audit exists (bin/vp_live.sh).
# SKILL step 2 is the whole mechanical job: bravo_user_audit.py --send (DMs Joshua through the outbox only when
# something needs him; ALREADY_SENT / SENT=none(clean) otherwise). SKILL step 1 (refresh hr/GUSTO_DISMISSED.json
# from the Gusto connector) has NO native path — no Gusto token on the Mac — so the existing file is used as-is
# and its age is logged (the script's own RUN_LOG line + this agent log). Step 4's OPEN_ITEMS row is left to the
# reader of the DM (the DM itself names the people and the store).
#   --render  = run without --send (writes <ym>.json/.mrkdwn.txt, sends nothing)
AGENT="monthly-bravo-user-audit"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
if [ "$1" = "--render" ]; then shift; "$PY" "$BIN/bravo_user_audit.py" "$@"; exit $?; fi
vp_live_gate "$AGENT"
vp_lock "$AGENT" 60
G="$OS_DIR/hr/GUSTO_DISMISSED.json"
[ -f "$G" ] && vlog "dismissed list on file: generated $("$PY" -c "import json;print(json.load(open('$G')).get('generated'))") (not refreshed natively — no Gusto token)" || vlog "no dismissed list on file — finding B uses roster only"
LINE=$("$PY" "$BIN/bravo_user_audit.py" --send "$@" 2>>"$VLOG/$AGENT.log") || { vlog "script failed: $LINE"; ledger "$AGENT" "The monthly Bravo logins check did not run." "no"; exit 1; }
vlog "$LINE"
exit 0
