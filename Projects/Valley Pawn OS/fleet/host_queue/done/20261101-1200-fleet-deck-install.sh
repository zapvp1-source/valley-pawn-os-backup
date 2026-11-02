#!/bin/bash
# VP Fleet Deck install (2026-11-01) — explicitly approved by Joshua in-session ("approve the fleet deck install").
# Allow-lists the 3 new bin/ scripts, then installs + loads com.valleypawn.fleet-deck (read-only status server on
# 127.0.0.1:8790) and com.valleypawn.fleet-deck-window (keeps the dashboard window open). Idempotent; posts nothing.
sleep 90
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/append_line.sh" "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/host_queue_allowlist.txt" "fleet_deck.py"
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/append_line.sh" "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/host_queue_allowlist.txt" "fleet_deck_run.sh"
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/append_line.sh" "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/host_queue_allowlist.txt" "fleet_deck_window.sh"
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.fleet-deck
sleep 15
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.fleet-deck-window
