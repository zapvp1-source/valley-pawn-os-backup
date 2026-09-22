#!/bin/bash
# Diagnose the remaining failures: items-to-price WAY stall, jewelry LEX wedge, and the
# three undiagnosed weeklies. Read-only.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "########## items-to-price: is WAY still short? ##########"
python3 "$BIN/csv_rows.py" items-to-price
echo "########## jewelry: LEX present today? ##########"
python3 "$BIN/csv_rows.py" jewelry-case-counts
echo "########## the 3 undiagnosed weeklies — their own words ##########"
python3 "$BIN/grep_skill.py" --ledger 2026-09-21
