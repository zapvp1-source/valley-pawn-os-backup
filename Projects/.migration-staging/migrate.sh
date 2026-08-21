#!/bin/bash
# Detached runner: quit Claude.app, apply registry_edit.py, relaunch Claude.app.
LOG="$HOME/Documents/Claude/Projects/.migration-staging/migrate.log"
exec >>"$LOG" 2>&1
echo "=== migrate.sh start $(date) ==="
sleep 5
osascript -e 'tell application "Claude" to quit' || true
sleep 10
if pgrep -x Claude >/dev/null; then
  echo "Claude still running after quit; waiting 10 more"
  sleep 10
fi
if pgrep -x Claude >/dev/null; then
  echo "ABORT: Claude.app would not quit; registry NOT edited (avoiding clobber)."
  exit 1
fi
python3 "$HOME/Documents/Claude/Projects/.migration-staging/registry_edit.py"
RC=$?
echo "registry_edit rc=$RC"
sleep 2
open -a Claude
echo "=== migrate.sh done $(date) ==="
