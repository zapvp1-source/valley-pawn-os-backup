#!/bin/bash
# Restart the Bravo watcher (loads the new IntakeDetail.ahk handler).
# Backgrounded so prlctl can't hang this interactive session. Bravo itself is not touched.
GUID='{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}'
nohup /usr/local/bin/prlctl exec "$GUID" --current-user powershell.exe -NoProfile -ExecutionPolicy Bypass \
  -File 'Y:\Documents\Claude\Projects\Bravo Data Extraction\_restart_watcher.ps1' \
  > /tmp/restart_watcher_now.log 2>&1 &
echo "restart launched (backgrounded), pid $!"
