#!/bin/bash
# Why did monday-bravo-combined-compile miss at 08:08 today when the data was on disk?
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== did the data-first override actually land in its SKILL? ====="
python3 "$BIN/grep_skill.py" monday-bravo-combined-compile "DATA-FIRST GATE OVERRIDE"
echo "===== ledger rows written today ====="
python3 "$BIN/grep_skill.py" --ledger 2026-09-21
