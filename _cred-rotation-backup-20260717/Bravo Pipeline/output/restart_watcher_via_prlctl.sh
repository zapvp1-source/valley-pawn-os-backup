#!/bin/bash
# Restart the Bravo watcher inside the running Windows 11 VM via prlctl.
# Pipeline pattern adopted from Scheduled/monday-bravo-combined-run/SKILL.md (Step 0 / Check 2).

set +e
PRLCTL="/usr/local/bin/prlctl"
VM_ID="{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}"
LOG=/tmp/restart_watcher_step.log
: > "$LOG"

echo "[step 1] verify prlctl + VM" >> "$LOG"
"$PRLCTL" list "$VM_ID" >> "$LOG" 2>&1
echo "  prlctl-list-exit=$?" >> "$LOG"

echo "[step 2] kill old AHK watchers" >> "$LOG"
"$PRLCTL" exec "$VM_ID" --current-user cmd /c "taskkill /F /IM AutoHotkey64.exe" >> "$LOG" 2>&1
echo "  taskkill-exit=$?" >> "$LOG"

sleep 3

echo "[step 3] launch fresh watcher" >> "$LOG"
"$PRLCTL" exec "$VM_ID" --current-user cmd /c 'start "" /B "C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe" "Y:\Documents\Claude\Projects\Bravo Data Extraction\bravo_watcher.ahk"' >> "$LOG" 2>&1
echo "  start-exit=$?" >> "$LOG"

sleep 8

echo "[step 4] confirm watcher.last_started.txt updated" >> "$LOG"
head -1 "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/logs/watcher.last_started.txt" >> "$LOG" 2>&1

cat "$LOG"
exit 0
