#!/bin/bash
LOG="$HOME/Documents/Claude/Projects/.migration-staging/migrate2.log"
exec >>"$LOG" 2>&1
echo "=== migrate2 start $(date) ==="
sleep 3
osascript -e 'tell application "Claude" to quit' || true
sleep 6
pkill -x Claude || true
sleep 2
pkill -f 'Claude Helper' || true
sleep 6
REG="$HOME/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/scheduled-tasks.json"
for i in 1 2 3 4 5 6; do
  if lsof "$REG" >/dev/null 2>&1; then echo "handles still open, wait $i"; sleep 5; else break; fi
done
pgrep -fl 'Claude Helper' && echo "WARN: helpers survive" || echo "helpers gone"
python3 "$HOME/Documents/Claude/Projects/.migration-staging/registry_edit.py"
echo "edit rc=$?"
python3 - <<'PY'
import json,os
p=os.path.expanduser("$HOME".replace("$HOME",os.path.expanduser("~"))+"/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/scheduled-tasks.json")
d=json.load(open(p)); print("post-edit count:",len(d["scheduledTasks"]))
PY
sleep 2
open -a Claude
echo "=== migrate2 done $(date) ==="
