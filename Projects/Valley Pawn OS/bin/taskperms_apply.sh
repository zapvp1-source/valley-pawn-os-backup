#!/bin/bash
# taskperms_apply.sh — created 2026-09-04
# Applies taskperms_registry_edit.py (read-only sibling approvals, fleet-wide) with
# Claude.app quiesced. Identical quiesce pattern to chromeperms_apply.sh / migrate3.sh
# (proven 2026-08-21). Fired ONCE by launchd (com.valleypawn.taskperms-oneshot) at 02:10,
# deliberately BEFORE the 04:00 bald-rock-15-day-contract fire so tomorrow's run is fixed.

LOG="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/taskperms_apply.log"
exec >>"$LOG" 2>&1
echo "=== taskperms_apply start $(date) ==="

REG="$HOME/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/scheduled-tasks.json"

# Don't start while a scheduled run is mid-flight (any Claude CLI child alive)
for i in 1 2 3 4 5 6; do
  if pgrep -f 'claude.*--scheduled|cli_session|claude-code' >/dev/null 2>&1; then
    echo "scheduled run active, wait $i"; sleep 60
  else
    break
  fi
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
if [ "$M1" != "$M2" ]; then
  echo "ABORT: registry still being written ($M1 -> $M2)"; open -a Claude; exit 1
fi
echo "registry quiet, editing"

/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/taskperms_registry_edit.py"
RC=$?
echo "edit rc=$RC"

# Roll back automatically if the edit produced unreadable JSON — never leave the
# fleet with a corrupt registry (fix-forward, Rule 15).
if ! /usr/bin/python3 -c "import json,sys; json.load(open('$REG'))" 2>/dev/null; then
  echo "ABORT: registry is not valid JSON after edit — restoring newest backup"
  NEWEST=$(ls -t "$REG".bak-taskperms-* 2>/dev/null | head -1)
  [ -n "$NEWEST" ] && cp -p "$NEWEST" "$REG" && echo "restored $NEWEST"
  open -a Claude; exit 1
fi

sleep 5
echo "-- relaunching app --"
open -a Claude
sleep 45

/usr/bin/python3 - <<'PY'
import json, os, time
p = os.path.expanduser('~/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/scheduled-tasks.json')
d = json.load(open(p)); st = d['scheduledTasks']
print('post-relaunch mtime:', time.ctime(os.path.getmtime(p)), 'count:', len(st))
print('enabled:', sum(1 for t in st if t.get('enabled')))
br = [t for t in st if t['id'] == 'bald-rock-15-day-contract']
if br:
    names = {a.get('toolName', '') for a in (br[0].get('approvedPermissions') or [])}
    need = 'mcp__8ff1eb8f-1c43-4cbb-bcb3-9167c3c96cc7__listRecipients'
    print('bald-rock approvals:', len(names))
    print('listRecipients present:', need in names, '  <-- the fix that matters')
PY

# self-remove the one-shot agent
launchctl bootout gui/$(id -u)/com.valleypawn.taskperms-oneshot 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/com.valleypawn.taskperms-oneshot.plist"
echo "=== taskperms_apply done $(date) ==="
