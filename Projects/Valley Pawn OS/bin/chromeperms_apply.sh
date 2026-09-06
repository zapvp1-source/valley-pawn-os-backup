#!/bin/bash
# Phase 0.4 runner — identical quiesce pattern to Projects/.migration-staging/migrate3.sh
# (proven 2026-08-21). Fired once by launchd (com.valleypawn.chromeperms-oneshot) at 02:10.
LOG="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/chromeperms_apply.log"
exec >>"$LOG" 2>&1
echo "=== chromeperms_apply start $(date) ==="
REG="$HOME/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/scheduled-tasks.json"
# Don't start while a scheduled run is mid-flight (any Claude CLI child alive)
for i in 1 2 3 4 5 6; do
  if pgrep -f 'claude.*--scheduled|cli_session|claude-code' >/dev/null 2>&1; then echo "scheduled run active, wait $i"; sleep 60; else break; fi
done
osascript -e 'tell application "Claude" to quit' || true
sleep 8
pkill -TERM -f 'Claude\.app' || true
sleep 6
pkill -KILL -f 'Claude\.app' || true
sleep 4
if pgrep -f 'Claude\.app' >/dev/null; then
  echo "ABORT: Claude.app processes still alive:"; pgrep -fl 'Claude\.app'
  open -a Claude; exit 1
fi
echo "all Claude.app processes dead"
M1=$(stat -f %m "$REG"); sleep 30; M2=$(stat -f %m "$REG")
if [ "$M1" != "$M2" ]; then echo "ABORT: registry still being written ($M1 -> $M2)"; open -a Claude; exit 1; fi
echo "registry quiet, editing"
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/chromeperms_registry_edit.py"
echo "edit rc=$?"
sleep 5
echo "-- relaunching app --"
open -a Claude
sleep 45
/usr/bin/python3 - <<'PY'
import json,os,time,collections
p=os.path.expanduser('~/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/scheduled-tasks.json')
d=json.load(open(p)); st=d['scheduledTasks']
print('post-relaunch mtime:',time.ctime(os.path.getmtime(p)),'count:',len(st))
print('chromePermissionMode:',dict(collections.Counter(t.get('chromePermissionMode') for t in st)))
print('northwest cron:',[t.get('cronExpression') for t in st if t['id']=='northwest-registered-agent-daily-check'])
PY
# self-remove the one-shot agent
launchctl bootout gui/$(id -u)/com.valleypawn.chromeperms-oneshot 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/com.valleypawn.chromeperms-oneshot.plist"
echo "=== chromeperms_apply done $(date) ==="
