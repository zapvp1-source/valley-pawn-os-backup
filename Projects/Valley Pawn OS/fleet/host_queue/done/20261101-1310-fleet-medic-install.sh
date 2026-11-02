#!/bin/bash
# fleet-medic install + Fleet Deck v2 restart (2026-11-01, Joshua: "create loops that fix items that come up as error").
# Starts OBSERVE-ONLY (fleet/state/fleet_medic_off exists) until the first passes are verified.
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/append_line.sh" "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/host_queue_allowlist.txt" "fleet_medic.py"
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/append_line.sh" "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/host_queue_allowlist.txt" "fleet_medic_run.sh"
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.fleet-deck --restart-only
sleep 20
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.fleet-medic
