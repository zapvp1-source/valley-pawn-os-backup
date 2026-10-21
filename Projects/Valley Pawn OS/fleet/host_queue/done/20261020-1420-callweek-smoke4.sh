#!/bin/bash
# comms review restart 2026-10-20: smoke 4 — narrative JSON fix (facts sanitized + repair); all 40 grades cached so this is narrative + render only, no DM
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/call_week_grade.py" --since 2026-10-12 --until 2026-10-18 --max-calls 40 --render --no-pull
