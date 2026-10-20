#!/bin/bash
set +e
echo "--- drive probe v2"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/w3_probe.py" drive
echo "--- scrap rankings render, fixed union"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/scrap_rankings_monthly.py" 2026-09 --render
echo "--- catchup render"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/catchup.py" --render
