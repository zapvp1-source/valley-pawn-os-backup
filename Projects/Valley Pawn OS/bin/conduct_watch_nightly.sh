#!/bin/bash
# launchd wrapper — com.valleypawn.conductwatch-nightly (Mon–Sat 19:20). Built 2026-10-31.
# Analyzes today's footage (screen -> verify -> audio -> clips), then applies retention. Writes files only; no Slack.
# Usage: conduct_watch_nightly.sh [YYYY-MM-DD] [extra analyze.py args]
AGENT="conductwatch-nightly"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
[ -n "$1" ] || vp_live_gate "$AGENT"
vp_lock "$AGENT" 900
DATE="${1:-$(date +%Y-%m-%d)}"; shift 2>/dev/null
TRIAL_END=$(/usr/bin/python3 -c "import json;print(json.load(open('$HOME/Documents/Claude/Projects/Store Conduct Watch/config.json')).get('trial_end','9999'))")
[[ "$DATE" > "$TRIAL_END" ]] && { vlog "trial ended $TRIAL_END — nothing to do"; exit 0; }
cd "$HOME/Documents/Claude/Projects/Store Conduct Watch" || exit 1
mkdir -p logs
PYV="$HOME/.vp-studio/conduct-watch-venv/bin/python"
# Catch-up (Hardening #4): a missed night (lock held, Mac asleep, crash) is analyzed before today's, up to 2 days back.
if [ $# -eq 0 ]; then
  for back in 2 1; do
    PD=$(date -v-${back}d -j -f %Y-%m-%d "$DATE" +%Y-%m-%d)
    if [ -n "$(open_stores "$PD")" ] && [ ! -f "reports/$PD/run.json" ] && [ -d "$HOME/.vp-studio/conduct-watch/frames" ] && ls -d "$HOME"/.vp-studio/conduct-watch/frames/*/*/"$PD" >/dev/null 2>&1; then
      vlog "catch-up analyze $PD"
      "$PYV" analyze.py "$PD" 2>&1 | tee -a "$VLOG/$AGENT.log" >> "logs/$AGENT.log"
      "$PYV" cleanup.py "$PD" >> "logs/$AGENT.log" 2>&1
    fi
  done
fi
vlog "analyze $DATE start"
"$PYV" analyze.py "$DATE" "$@" 2>&1 | tee -a "$VLOG/$AGENT.log" >> "logs/$AGENT.log"
RC=${PIPESTATUS[0]}
case " $* " in *" --store "*) vlog "test run ($*) — no cleanup, no ledger"; exit $RC ;; esac
"$PYV" cleanup.py "$DATE" >> "logs/$AGENT.log" 2>&1
grep -q '"complete": true' "reports/$DATE/run.json" 2>/dev/null || { [ -n "$(open_stores "$DATE")" ] && ledger "$AGENT" "Camera watch analysis for $DATE did not finish (rc=$RC)" "no"; }
vlog "analyze $DATE end rc=$RC"
exit $RC
