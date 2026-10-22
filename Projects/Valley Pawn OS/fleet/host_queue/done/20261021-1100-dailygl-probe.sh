#!/bin/bash
# 2026-10-21 daily Bravo->QBO build: read-only probe + September monthly entry DRY RUN (no --go)
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_daily_gl.py" --probe
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_bravo_month.sh" 2026-09
