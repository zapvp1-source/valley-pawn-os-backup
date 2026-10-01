#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/run_trace.py" daily-items-to-price 2026-09-30 20
python3 "$BIN/skill_shell_steps.py" daily-items-to-price
python3 "$BIN/skill_dump.py" daily-items-to-price 14000
