#!/bin/bash
echo ===== XLSX
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/w2_probe.py" xlsx "/Users/joshuadavis/Desktop/Claude Back Up/Claude 4 back up/Valley_Pawn_Returns_Trend.xlsx" 25
echo ===== RETURNS HIST
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/w2_probe.py" hist C03BNUN2SDA 24
echo ===== WRS HIST
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/w2_probe.py" hist C0B1K4WK2HZ 20
echo ===== HEALTH LS
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/w2_probe.py" ls "/Users/joshuadavis/Documents/Claude/Projects/Health Optimization" 40
