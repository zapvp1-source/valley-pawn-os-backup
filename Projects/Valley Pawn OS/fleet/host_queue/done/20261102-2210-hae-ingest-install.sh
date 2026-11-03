#!/bin/bash
# Install the Apple Health auto-export ingest agent (Joshua 2026-11-02: "set up the auto export"). Only allow-listed calls.
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.hae-ingest
sleep 5
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.hae-ingest --restart-only
sleep 45
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" "/Users/joshuadavis/Library/Logs/valleypawn/hae-ingest.log"
