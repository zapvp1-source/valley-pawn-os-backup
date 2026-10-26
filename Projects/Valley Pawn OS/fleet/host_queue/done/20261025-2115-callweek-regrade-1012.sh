#!/bin/bash
# 2026-10-25 re-grade Oct 12-18 under the 10/25 loan/phone rules into a FRESH folder (old week_2026-10-12/grades untouched). Render only: no DM, no Drive, no CHANGELOG line.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
CA="$HOME/Documents/Claude/Projects/Call Analysis"
python3 "$BIN/call_week_grade.py" --since 2026-10-12 --until 2026-10-18 --no-pull --render --week-dir "$CA/week_2026-10-12_regrade_rules20261025"
