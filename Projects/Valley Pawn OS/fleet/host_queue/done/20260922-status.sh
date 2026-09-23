#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "##### 1. chekkit permission fix (02:10) — did it apply and SURVIVE relaunch? #####"
python3 "$BIN/inspect_path.py" "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/chekkitperms_apply.log" --lines 40
echo "##### 2. nightly doctor #####"
python3 "$BIN/inspect_path.py" "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/doctor/2026-09-22.md" --lines 6
echo "##### 3. what posted, last 3 days #####"
python3 "$BIN/recent_truth.py" --days 3
echo "##### 4. Monday-dated pull certificate #####"
python3 "$BIN/inspect_path.py" "$HOME/Documents/Claude/Projects/Bravo Data Extraction/logs/_monday_pull_status_2026-09-21.txt" --lines 10
echo "##### 5. ledger rows since Batch 1 went on #####"
python3 "$BIN/grep_skill.py" --ledger 2026-09-22
