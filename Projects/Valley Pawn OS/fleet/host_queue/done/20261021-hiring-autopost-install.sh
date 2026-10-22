#!/bin/bash
# Install + first run of the hiring auto-post agent (Joshua 2026-10-21). RunAtLoad fires the first live run.
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/hiring_autopost.py" --render
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.hiring-autopost
sleep 90
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" "/Users/joshuadavis/Library/Logs/valleypawn/hiring-autopost.log"
