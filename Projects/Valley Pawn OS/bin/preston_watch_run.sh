#!/bin/bash
# launchd wrapper for preston_watch.py (invoked via ~/bin/vp-runner for TCC access to ~/Documents).
exec /usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/preston_watch.py" "$@"
