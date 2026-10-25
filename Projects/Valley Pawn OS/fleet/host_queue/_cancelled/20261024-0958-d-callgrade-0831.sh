#!/bin/bash
# 2026-10-24 November-meeting call clips: grade every recorded call not yet graded (2026-08-31..2026-09-08). --render = no DM, no Drive copy, no CHANGELOG.
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/call_week_grade.py" --since 2026-08-31 --until 2026-09-08 --render --no-texts
