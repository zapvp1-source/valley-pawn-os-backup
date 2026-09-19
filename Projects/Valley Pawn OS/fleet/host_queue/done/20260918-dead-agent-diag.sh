#!/bin/bash
# Diagnose compliance-brief (channel_not_found since 9/14) and cloudcover (48.7% real defect). Read-only.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "########## compliance-brief agent ##########"
python3 "$BIN/inspect_path.py" "$HOME/Library/LaunchAgents/com.valleypawn.compliance-brief.plist" --lines 30
echo "########## its log ##########"
python3 "$BIN/inspect_path.py" "$HOME/Library/Logs/valleypawn/compliance-brief.log" --lines 25
echo "########## cloudcover task ##########"
python3 "$BIN/inspect_path.py" "$HOME/Documents/Claude/Scheduled/daily-cloudcover-check"
echo "########## chrome extension watchdog log ##########"
python3 "$BIN/inspect_path.py" "$HOME/Library/Logs/valleypawn/chrome-extension-watchdog.log" --lines 20
