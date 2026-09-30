#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/task_preflight.py" --disabled --mac-days 60 --json "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/preflight_disabled_20260929.json"
