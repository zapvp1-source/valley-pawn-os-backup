#!/bin/bash
# Fleet diet applier — same proven quiesce/edit/relaunch pattern as bin/chromeperms_apply.sh (2026-09-09).
# Run via the host job queue (fleet/host_queue/) ONLY after the registry has been restored to the
# full fleet (>=150 tasks) and no other quiesce/relaunch job is pending. The edit script refuses
# a partial/empty registry on its own, so a premature run is a no-op, not damage.
LOG="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/fleet_diet_apply.log"
exec >>"$LOG" 2>&1
echo "=== fleet_diet_apply start $(date) ==="
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
REG=$(ls -t "$HOME/Library/Application Support/Claude/local-agent-mode-sessions"/*/*/scheduled-tasks.json 2>/dev/null | head -1)
[ -n "$REG" ] || { echo "ABORT: no registry"; exit 1; }
/usr/bin/python3 "$BIN/fleet_diet_registry_edit.py" --dry-run || { echo "ABORT: dry-run refused"; exit 1; }
for i in 1 2 3 4 5 6; do
  if pgrep -f 'claude.*--scheduled|cli_session|claude-code' >/dev/null 2>&1; then echo "scheduled run active, wait $i"; sleep 60; else break; fi
done
osascript -e 'tell application "Claude" to quit' || true
sleep 8; pkill -TERM -f 'Claude\.app' || true; sleep 6; pkill -KILL -f 'Claude\.app' || true; sleep 4
if pgrep -f 'Claude\.app' >/dev/null; then echo "ABORT: Claude.app still alive"; open -a Claude; exit 1; fi
M1=$(stat -f %m "$REG"); sleep 30; M2=$(stat -f %m "$REG")
if [ "$M1" != "$M2" ]; then echo "ABORT: registry still being written"; open -a Claude; exit 1; fi
/usr/bin/python3 "$BIN/fleet_diet_registry_edit.py"; echo "edit rc=$?"
sleep 5; open -a Claude; sleep 60
/usr/bin/python3 - <<'PY'
import json,glob,os,time
p=sorted(glob.glob(os.path.expanduser('~/Library/Application Support/Claude/local-agent-mode-sessions/*/*/scheduled-tasks.json')),key=os.path.getmtime)[-1]
d=json.load(open(p)); st=d['scheduledTasks']
print('post-relaunch mtime:',time.ctime(os.path.getmtime(p)),'tasks:',len(st),'enabled:',sum(1 for t in st if t.get('enabled')))
PY
grep -c ZodError "$HOME/Library/Logs/Claude/main.log" 2>/dev/null | sed 's/^/ZodError lines in main.log: /'
echo "=== fleet_diet_apply done $(date) ==="
