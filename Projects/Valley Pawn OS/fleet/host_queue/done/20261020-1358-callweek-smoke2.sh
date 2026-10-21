#!/bin/bash
# comms review restart 2026-10-20: smoke-test the native weekly phone/text review on 10/12-10/18 now that the week folder is complete (render only, 40 calls, no DM, no CHANGELOG line)
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/call_week_grade.py" --since 2026-10-12 --until 2026-10-18 --max-calls 40 --render --no-pull
