#!/bin/bash
# Relaunch Bravo + watcher via the proven _relaunch_bravo_and_watcher.ps1.
PRLCTL="/usr/local/bin/prlctl"
VM="{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}"
# kill the leftover island AHK (the warning-dialog process) so it stops blocking
"$PRLCTL" exec "$VM" --current-user powershell.exe -NoProfile -Command "Get-Process AutoHotkey64 -ErrorAction SilentlyContinue | Where-Object { ((Get-WmiObject Win32_Process -Filter \"ProcessId=\$(\$_.Id)\").CommandLine) -like '*Loans75_gridread_island*' } | Stop-Process -Force" </dev/null >/tmp/killisland.log 2>&1 &
sleep 3
"$PRLCTL" exec "$VM" --current-user powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'Y:\Documents\Claude\Projects\Bravo Data Extraction\_relaunch_bravo_and_watcher.ps1' </dev/null >/tmp/relaunch.log 2>&1 &
PID=$!
( sleep 15; kill -9 "$PID" 2>/dev/null ) &
sleep 14
echo "relaunch issued"; cat /tmp/relaunch.log 2>&1 | head -20
