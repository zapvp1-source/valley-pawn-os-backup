#!/bin/bash
# Fire prlctl restart commands ASYNC so the calling osascript returns fast.
# Per BRAVO_KNOWN_ISSUES.md prlctl exec of console programs can hang on terminal allocation.
# Drop a log so we can confirm what happened after the fact.

LOG=/tmp/restart_watcher_async.log
: > "$LOG"
echo "started=$(date)" >> "$LOG"

nohup bash -c '
  PRLCTL="/usr/local/bin/prlctl"
  VM="{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}"
  exec >>/tmp/restart_watcher_async.log 2>&1
  echo "kill phase: $(date)"
  "$PRLCTL" exec "$VM" --current-user cmd /c "taskkill /F /IM AutoHotkey64.exe"
  echo "kill exit=$?"
  sleep 3
  echo "launch phase: $(date)"
  "$PRLCTL" exec "$VM" --current-user cmd /c "start \"\" /B \"C:\\Program Files\\AutoHotkey\\v2\\AutoHotkey64.exe\" \"Y:\\Documents\\Claude\\Projects\\Bravo Data Extraction\\bravo_watcher.ahk\""
  echo "launch exit=$?"
  sleep 8
  echo "watcher.last_started.txt: $(head -1 \"/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/logs/watcher.last_started.txt\")"
  echo "done=$(date)"
' >/dev/null 2>&1 &

echo "spawned-pid=$!" >> "$LOG"
echo "exiting=$(date)" >> "$LOG"
exit 0
