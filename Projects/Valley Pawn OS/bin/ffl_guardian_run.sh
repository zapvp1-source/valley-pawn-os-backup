#!/bin/bash
# launchd wrapper for the FFL Guardian (invoked via ~/bin/vp-runner for TCC
# access to ~/Documents and ~/Library/Mail). Logs go to ~/Library/Logs/valleypawn/
# so launchd itself never has to open a file inside ~/Documents.
exec /usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/ffl_guardian.py" "$@"
