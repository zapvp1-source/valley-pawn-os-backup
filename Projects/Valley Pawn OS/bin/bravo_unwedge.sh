#!/bin/bash
# bravo_unwedge.sh — close console windows covering Bravo, then run the health gate. Allow-listed.
AGENT=bravo-unwedge; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vlog "closing stray terminals: $(bravo_close_terminals)"; sleep 3
vlog "health gate: $(health_gate 420)"
