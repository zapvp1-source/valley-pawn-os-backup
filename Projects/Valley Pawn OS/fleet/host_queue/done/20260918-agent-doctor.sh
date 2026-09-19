#!/bin/bash
# Cross-check every launchd agent against the program it runs. Read-only; unloads nothing.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/agent_doctor.py"
