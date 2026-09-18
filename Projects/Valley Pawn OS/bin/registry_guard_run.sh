#!/bin/bash
# launchd wrapper for the Registry Guard (invoked via ~/bin/vp-runner for TCC access to
# ~/Documents). Logs to ~/Library/Logs/valleypawn/ so launchd itself never opens a file
# inside ~/Documents. Also drains the host job queue first (detached, non-blocking) so a
# queued host job never waits more than 5 minutes even if preston-watch is down.
OS_BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
/bin/bash "$OS_BIN/host_queue_spawn.sh" >/dev/null 2>&1 || true
exec /usr/bin/python3 "$OS_BIN/registry_guard.py" "$@"
