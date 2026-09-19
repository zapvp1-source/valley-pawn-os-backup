#!/bin/bash
# Diagnose the broken dashboard-data-collector agent before touching anything. Read-only.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/inspect_path.py" "$HOME/Documents/Claude/Scheduled/dashboard-data-collector"
python3 "$BIN/inspect_path.py" "$HOME/Library/LaunchAgents/com.valleypawn.dashboarddatacollector.plist" --lines 45
python3 "$BIN/inspect_path.py" "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/compliance-brief-note.txt"
