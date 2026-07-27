#!/bin/bash
# Variant — skip taskkill, rely on AHK #SingleInstance Force.
# Just exec the AHK relaunch with start "" /B (fully detached).
PRLCTL="/usr/local/bin/prlctl"
VM="{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}"
LOG=/tmp/restart_watcher_v2.log
: > "$LOG"
echo "v2 started=$(date)" >> "$LOG"

# Single prlctl exec, detached child. The trick: redirect input to /dev/null
# so prlctl doesn't wait for an interactive terminal.
"$PRLCTL" exec "$VM" --current-user \
  cmd /c "start \"\" /B \"C:\\Program Files\\AutoHotkey\\v2\\AutoHotkey64.exe\" \"Y:\\Documents\\Claude\\Projects\\Bravo Data Extraction\\bravo_watcher.ahk\"" \
  </dev/null >>"$LOG" 2>&1 &
PRLPID=$!
echo "prlctl-pid=$PRLPID" >> "$LOG"

# Give prlctl 30s; if it hangs past that, move on.
( sleep 30; kill -9 "$PRLPID" 2>/dev/null; echo "killed-stuck-prlctl" >> "$LOG" ) &

wait "$PRLPID" 2>/dev/null
echo "prlctl-finished=$(date)" >> "$LOG"
sleep 5
echo "watcher.last_started: $(head -1 '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/logs/watcher.last_started.txt')" >> "$LOG"
cat "$LOG"
exit 0
