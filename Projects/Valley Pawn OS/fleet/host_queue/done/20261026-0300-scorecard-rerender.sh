#!/bin/bash
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/fleet_scorecard.py" --render 2026-10-23 --detail
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/fleet_scorecard.py" --render 2026-10-24 --detail
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/fleet_scorecard.py" --render 2026-10-25 --detail
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" fleet-scorecard.log 30
