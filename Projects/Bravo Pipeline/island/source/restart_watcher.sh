#!/bin/bash
# Restart the prod watcher via the proven _restart_watcher.ps1 (Y:-aware, schtasks).
PRLCTL="/usr/local/bin/prlctl"
VM="{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}"
"$PRLCTL" exec "$VM" --current-user powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'Y:\Documents\Claude\Projects\Bravo Data Extraction\_restart_watcher.ps1' </dev/null >/tmp/wrestart.log 2>&1 &
PID=$!
( sleep 16; kill -9 "$PID" 2>/dev/null ) &
sleep 14
echo "restart issued (pid=$PID)"
