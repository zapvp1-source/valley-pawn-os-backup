#!/bin/bash
# Joshua 10/21 "go": post the September 2026 monthly Bravo entries (validated dry run 10:16, company-wide imbalance 0.00), then a RENDER of the daily poster for 10/20 (no QBO write)
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_bravo_month.sh" 2026-09 --go
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_daily_gl.py" --render --day 2026-10-20
