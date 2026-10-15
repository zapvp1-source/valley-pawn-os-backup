#!/bin/bash
echo "=== render 2026-10-13 ==="
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/fleet_scorecard.py" --render 2026-10-13 --detail
echo "=== today partial ==="
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/fleet_scorecard.py" --today --detail
echo "=== render 2026-10-12 ==="
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/fleet_scorecard.py" --render 2026-10-12 --detail
