#!/bin/bash
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.fleet-scorecard
echo "=== send 2026-10-13 ==="
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/fleet_scorecard.py" --send 2026-10-13
echo "=== second send attempt must refuse ==="
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/fleet_scorecard.py" --send 2026-10-13
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/host_diag.sh" agents
