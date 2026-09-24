#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "##### outbox — did last night's posts go through the bot? #####"
python3 "$BIN/inspect_path.py" "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/outbox/outbox.log" --lines 12
echo "##### last 3 days #####"
python3 "$BIN/recent_truth.py" --days 3
echo "##### ledger since yesterday #####"
python3 "$BIN/grep_skill.py" --ledger 2026-09-22
python3 "$BIN/grep_skill.py" --ledger 2026-09-23
echo "##### doctor #####"
python3 "$BIN/inspect_path.py" "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/doctor/2026-09-23.md" --lines 4
