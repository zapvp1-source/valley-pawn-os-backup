#!/bin/bash
PRLCTL="/usr/local/bin/prlctl"
VM="{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}"
"$PRLCTL" exec "$VM" --current-user powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'Y:\Documents\Claude\Projects\Bravo Pipeline\island\source\cleanup.ps1' </dev/null >/tmp/island_cleanup.log 2>&1 &
PID=$!
( sleep 12; kill -9 "$PID" 2>/dev/null ) &
sleep 12
echo "cleanup issued"; cat /tmp/island_cleanup.log 2>&1
