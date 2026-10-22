#!/bin/bash
# launchd wrapper for the weekly read-only FFL drift check (via ~/bin/vp-runner for TCC). Added 2026-10-21.
exec /usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/ffl_drift_check.py" "$@"
