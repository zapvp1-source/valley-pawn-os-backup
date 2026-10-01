#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/skill_shell_steps.py" document-photos-index-refresh nightly-desktop-cleanup vp-dashboard-refresh asset-recovery-daily-refresh
python3 "$BIN/skill_dump.py" nightly-desktop-cleanup 6000
python3 "$BIN/skill_dump.py" vp-dashboard-refresh 7000
