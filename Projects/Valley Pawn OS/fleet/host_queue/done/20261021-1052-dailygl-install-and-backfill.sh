#!/bin/bash
# Joshua 10/21 "go": install com.valleypawn.bravo-daily-gl (00:45 + 03:15) LIVE, then kick one run now = backfill 10/1..10/20 (stops 19:45, rest tonight)
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.bravo-daily-gl
sleep 5
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.bravo-daily-gl --restart-only
