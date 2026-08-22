#!/bin/bash
# launchd wrapper for mac_weekly_maintenance (invoked via ~/bin/vp-runner for
# TCC access to ~/Documents). Logs to ~/Library/Logs/valleypawn/.
exec /usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/mac_weekly_maintenance.py" "$@"
