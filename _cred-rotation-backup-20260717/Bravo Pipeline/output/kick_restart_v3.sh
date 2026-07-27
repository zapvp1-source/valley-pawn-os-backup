#!/bin/bash
# v3: invoke _restart_watcher.ps1 which uses Windows Scheduled Tasks
# under the hood to bypass the prlctl exec terminal-grab issue.
# Single prlctl call, async + 25s timeout cap.
PRLCTL="/usr/local/bin/prlctl"
VM="{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}"
LOG=/tmp/restart_watcher_v3.log
: > "$LOG"
echo "v3 started=$(date)" >> "$LOG"

"$PRLCTL" exec "$VM" --current-user \
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'Y:\Documents\Claude\Projects\Bravo Data Extraction\_restart_watcher.ps1' \
  </dev/null >>"$LOG" 2>&1 &
PID=$!
echo "prlctl-pid=$PID" >> "$LOG"

# 25s timeout
( sleep 25; kill -9 "$PID" 2>/dev/null && echo "killed-after-25s" >> "$LOG" ) &

wait "$PID" 2>/dev/null
echo "prlctl-finished=$(date)" >> "$LOG"
sleep 8
echo "watcher.last_started: $(head -1 '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/logs/watcher.last_started.txt')" >> "$LOG"
cat "$LOG"
exit 0
