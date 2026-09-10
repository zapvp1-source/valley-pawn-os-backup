#!/bin/bash
# One-shot: quiesce Claude.app, register connector-health-daily, relaunch. Fired once by launchd
# (com.valleypawn.connector-health-register-oneshot) at 02:10. Same quiesce pattern as
# chromeperms_apply.sh (proven 2026-09-04). chrome-extension-watchdog relaunches Claude if this fails.
LOG="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/connector_health_register.log"
exec >>"$LOG" 2>&1
echo "=== connector_health_register start $(date) ==="
for i in 1 2 3 4 5 6; do
  if pgrep -f 'claude.*--scheduled|cli_session|claude-code' >/dev/null 2>&1; then echo "scheduled run active, wait $i"; sleep 60; else break; fi
done
osascript -e 'tell application "Claude" to quit' || true
sleep 8; pkill -TERM -f 'Claude\.app' || true; sleep 6; pkill -KILL -f 'Claude\.app' || true; sleep 4
if pgrep -f 'Claude\.app' >/dev/null; then echo "ABORT: Claude.app still alive"; open -a Claude; exit 1; fi
REG=$(ls "$HOME/Library/Application Support/Claude/local-agent-mode-sessions"/*/*/scheduled-tasks.json | grep -v bak | head -1)
M1=$(stat -f %m "$REG"); sleep 30; M2=$(stat -f %m "$REG")
if [ "$M1" != "$M2" ]; then echo "ABORT: registry still being written"; open -a Claude; exit 1; fi
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/connector_health_register.py"; echo "edit rc=$?"
sleep 5; open -a Claude; sleep 45
/usr/bin/python3 - <<'PY'
import json,glob
p=[c for c in glob.glob('/Users/joshuadavis/Library/Application Support/Claude/local-agent-mode-sessions/*/*/scheduled-tasks.json') if '.bak' not in c][0]
st=json.load(open(p))['scheduledTasks']
print('post-relaunch count:',len(st),'connector-health-daily present:',any(t['id']=='connector-health-daily' for t in st))
PY
launchctl bootout gui/$(id -u)/com.valleypawn.connector-health-register-oneshot 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/com.valleypawn.connector-health-register-oneshot.plist"
echo "=== connector_health_register done $(date) ==="
