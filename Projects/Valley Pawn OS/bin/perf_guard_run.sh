#!/bin/bash
# launchd wrapper for perf_guard (invoked via ~/bin/vp-runner for TCC access
# to ~/Documents). Logs to ~/Library/Logs/valleypawn/.
exec /usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/perf_guard.py" "$@"
