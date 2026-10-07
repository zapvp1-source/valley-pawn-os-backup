#!/bin/bash
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" oura-daily-import.log 45
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" catchup.log 5
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" mac_maintenance.log 8
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" chrome-extension-watchdog.log 5
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/log_triage.py" --days 7
