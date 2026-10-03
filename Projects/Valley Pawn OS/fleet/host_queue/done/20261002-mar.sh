#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/run_trace.py" monthly-analytics-report 2026-10-01 15
python3 "$BIN/skill_shell_steps.py" monthly-analytics-report
python3 "$BIN/skill_dump.py" monthly-analytics-report 9000
