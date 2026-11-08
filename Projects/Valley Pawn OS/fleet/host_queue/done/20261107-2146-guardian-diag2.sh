#!/bin/bash
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/inspect_path.py" "$HOME/Library/LaunchAgents/com.valleypawn.ebay-efficiency-weekly.plist" --lines 60
echo "---LOG---"
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/inspect_path.py" "$HOME/Library/Logs/valleypawn/ebay-efficiency-weekly.log" --lines 40
