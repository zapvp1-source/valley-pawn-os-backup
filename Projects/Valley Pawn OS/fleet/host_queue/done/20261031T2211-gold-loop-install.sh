#!/bin/bash
# Gold plan operating loop — install the two native agents and produce the first scorecard (2026-10-31).
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/install_agent.sh" com.valleypawn.intake-backfill
bash "$BIN/install_agent.sh" com.valleypawn.gold-scorecard
bash "$BIN/gold_scorecard.sh" --end 2026-10-25
bash "$BIN/gold_scorecard.sh"
echo GOLD_LOOP_INSTALL_DONE
