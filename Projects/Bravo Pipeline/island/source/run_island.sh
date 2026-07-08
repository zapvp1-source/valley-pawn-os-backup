#!/bin/bash
# Launch the island grid-read AHK via the schtasks-based ps1 (proven UI-interactive path).
PRLCTL="/usr/local/bin/prlctl"
VM="{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}"
rm -f "/Users/joshuadavis/Documents/Claude/Projects/Bravo Pipeline/island/output/loans75-gridread.log" 2>/dev/null

"$PRLCTL" exec "$VM" --current-user powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'Y:\Documents\Claude\Projects\Bravo Pipeline\island\source\island_run.ps1' </dev/null >/tmp/island_launch.log 2>&1 &
PID=$!
( sleep 15; kill -9 "$PID" 2>/dev/null ) &
sleep 15
echo "launch attempted; client pid=$PID"
echo "client log:"; cat /tmp/island_launch.log 2>&1
