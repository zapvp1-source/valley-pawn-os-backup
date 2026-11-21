#!/bin/bash
# launchd wrapper for joshua_text_alert.py (run via ~/bin/vp-runner for TCC access to ~/Documents).
exec /usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/joshua_text_alert.py" "$@"
