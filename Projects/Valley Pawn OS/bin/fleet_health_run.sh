#!/bin/bash
# launchd wrapper for the Fleet Health Sentinel (invoked via ~/bin/vp-runner
# for TCC access to ~/Documents). Logs to ~/Library/Logs/valleypawn/ so
# launchd itself never has to open a file inside ~/Documents.
exec /usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/fleet_health_sentinel.py" "$@"
