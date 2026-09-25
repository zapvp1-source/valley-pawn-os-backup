#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/run_trace.py" daily-dress-code-check 2026-09-24 40
python3 "$BIN/run_trace.py" daily-dress-code-check 2026-09-22 40
python3 "$BIN/grep_skill.py" daily-dress-code-check "passkey"
python3 "$BIN/grep_skill.py" daily-dress-code-check "Try another way"
python3 "$BIN/grep_skill.py" daily-dress-code-check "password"
