#!/bin/bash
# launchd wrapper for the Disk Health Sentinel (invoked via ~/bin/vp-runner for TCC access to
# ~/Documents). Logs to ~/Library/Logs/valleypawn/ so launchd itself never opens a file inside
# ~/Documents directly.
exec /usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/disk_health_sentinel.py" "$@"
