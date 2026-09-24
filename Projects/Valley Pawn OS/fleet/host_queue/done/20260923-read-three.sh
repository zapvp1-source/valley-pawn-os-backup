#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/inspect_path.py" "$HOME/Documents/Claude/Scheduled/backup-health-watchdog/SKILL.md" --lines 120
python3 "$BIN/inspect_path.py" "$HOME/Documents/Claude/Scheduled/oura-daily-import/SKILL.md" --lines 90
python3 "$BIN/inspect_path.py" "$HOME/Documents/Claude/Scheduled/health-records-intake/SKILL.md" --lines 90
