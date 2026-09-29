#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
B="$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/skill_blocks/outbox_any_destination.md"
python3 "$BIN/install_skill_block.py" connector-health-daily "$B" --apply
python3 "$BIN/install_skill_block.py" monthly-analytics-report "$B" --apply
python3 "$BIN/install_skill_block.py" monthly-analytics-watchdog "$B" --apply
python3 "$BIN/install_skill_block.py" bonus-month-close "$B" --apply
python3 "$BIN/install_skill_block.py" bonus-month-close-pull "$B" --apply
python3 "$BIN/install_skill_block.py" google-reviews-post-watchdog "$B" --apply
python3 "$BIN/install_skill_block.py" missed-call-text-report "$B" --apply
python3 "$BIN/install_skill_block.py" weekly-markdown-verification-pull "$B" --apply
python3 "$BIN/install_skill_block.py" weekly-markdown-verification-review "$B" --apply
python3 "$BIN/task_preflight.py"
