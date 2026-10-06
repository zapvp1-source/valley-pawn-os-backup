#!/bin/bash
echo "=== ITP"
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/items_to_price.py" --render
echo "=== NICS"
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/nics_weekly_mtd.py" --render
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/nics_weekly_mtd.py" --render --end 2026-09-28
echo "=== KPI"
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/store_kpis_weekly.py" --render --end 2026-10-04
echo "=== LAY"
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/layaway_yield_weekly.py" --render --end 2026-10-04
