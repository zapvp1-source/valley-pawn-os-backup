#!/bin/bash
# finish 10/20 HAR+LEX (store-combo flake), then cross-check: one Bravo range GL 10/1..10/20 per store vs the sum of the 78+ daily entries
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_daily_gl.py" --day 2026-10-20
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_daily_gl.py" --check 2026-10-01..2026-10-20
