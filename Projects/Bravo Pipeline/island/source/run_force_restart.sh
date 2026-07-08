#!/bin/bash
# Force-kill the stuck Bravo and relaunch clean + watcher.
PRLCTL="/usr/local/bin/prlctl"
VM="{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}"
"$PRLCTL" exec "$VM" --current-user cmd /c "taskkill /F /IM Bravo.exe" </dev/null >/tmp/killbravo.log 2>&1 &
sleep 6
"$PRLCTL" exec "$VM" --current-user powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'Y:\Documents\Claude\Projects\Bravo Data Extraction\_relaunch_bravo_and_watcher.ps1' </dev/null >/tmp/relaunch2.log 2>&1 &
PID=$!
( sleep 16; kill -9 "$PID" 2>/dev/null ) &
sleep 15
echo "=== killbravo ==="; cat /tmp/killbravo.log 2>&1
echo "=== relaunch ==="; cat /tmp/relaunch2.log 2>&1 | head -12
