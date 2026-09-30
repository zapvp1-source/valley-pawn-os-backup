#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/task_preflight.py" --mac-days 14 --json "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/preflight_20260929_eve.json"
python3 "$BIN/agent_doctor.py"
