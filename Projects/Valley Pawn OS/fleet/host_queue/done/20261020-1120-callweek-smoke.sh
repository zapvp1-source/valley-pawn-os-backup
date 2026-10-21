#!/bin/bash
# comms review 2026-10-20: smoke-test the native weekly phone/text review on last week (Oct 12-18), 40 calls, render only (no DM, no CHANGELOG line)
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/call_week_grade.py" --since 2026-10-12 --until 2026-10-18 --max-calls 40 --render --no-pull
