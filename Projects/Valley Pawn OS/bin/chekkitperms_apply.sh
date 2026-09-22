#!/bin/bash
# chekkitperms_apply.sh — quiesce Claude.app, apply the two-task Chekkit permission fix, relaunch.
# Same proven quiesce pattern as chromeperms_apply.sh (2026-09-04) and migrate3.sh (2026-08-21).
# Fires ONCE from com.valleypawn.chekkitperms-oneshot at 02:10, because a live edit does not hold.
LOG="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/chekkitperms_apply.log"
exec >>"$LOG" 2>&1
echo "=== chekkitperms_apply start $(date) ==="
REG="$HOME/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/scheduled-tasks.json"
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
  echo "ABORT: Claude.app still alive:"; pgrep -fl 'Claude\.app'; open -a Claude; exit 1
fi
echo "all Claude.app processes dead"
M1=$(stat -f %m "$REG"); sleep 30; M2=$(stat -f %m "$REG")
if [ "$M1" != "$M2" ]; then echo "ABORT: registry still being written ($M1 -> $M2)"; open -a Claude; exit 1; fi
echo "registry quiet, editing"
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/chromeperms_fix_20260921.py"
rc=$?
echo "edit rc=$rc"
sleep 5
echo "-- relaunching app --"
open -a Claude
sleep 45
# Verify the change SURVIVED the relaunch — the fleet diet looked fine until the app resynced.
/usr/bin/python3 - <<'PY'
import json, os
REG = os.path.expanduser("~/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/scheduled-tasks.json")
v = {t.get("id"): t for t in json.load(open(REG))["scheduledTasks"]}
for tid in ("review-obtained-last-week", "google-reviews-post-watchdog"):
    t = v.get(tid, {})
    print("POST-RELAUNCH %-30s mode=%r domains=%s" % (tid, t.get("chromePermissionMode"), t.get("chromeAllowedDomains")))
PY
echo "=== chekkitperms_apply end $(date) ==="
