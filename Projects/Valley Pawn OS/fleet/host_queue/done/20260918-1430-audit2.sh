#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
/usr/bin/python3 "$BIN/vp_audit.py" --days 60 --json "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/AUDIT_2026-09-18.json"
