#!/bin/bash
LOG="$HOME/Documents/Claude/Projects/.migration-staging/migrate3.log"
exec >>"$LOG" 2>&1
echo "=== migrate3 start $(date) ==="
sleep 4
REG="$HOME/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/scheduled-tasks.json"
# Kill the entire Claude.app process tree (matches only /Applications/Claude.app paths)
pkill -TERM -f 'Claude\.app' || true
sleep 6
pkill -KILL -f 'Claude\.app' || true
sleep 4
if pgrep -f 'Claude\.app' >/dev/null; then
  echo "ABORT: Claude.app processes still alive:"; pgrep -fl 'Claude\.app'
  open -a Claude
  exit 1
fi
echo "all Claude.app processes dead"
M1=$(stat -f %m "$REG"); sleep 30; M2=$(stat -f %m "$REG")
if [ "$M1" != "$M2" ]; then echo "ABORT: registry still being written (mtime moved $M1 -> $M2)"; open -a Claude; exit 1; fi
echo "registry quiet, editing"
python3 "$HOME/Documents/Claude/Projects/.migration-staging/registry_edit.py"
echo "edit rc=$?"
sleep 30
python3 "$HOME/Documents/Claude/Projects/.migration-staging/verify_reg.py"
echo "-- relaunching app --"
open -a Claude
sleep 40
python3 "$HOME/Documents/Claude/Projects/.migration-staging/verify_reg.py"
echo "=== migrate3 done $(date) ==="
