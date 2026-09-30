#!/bin/bash
# HOST JOB — delete the exact-duplicate 2026-08 row (row 15) from the FFL Transfer Trend sheet (2026-09-29)
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/ffl_trend_dedupe.py" --apply
