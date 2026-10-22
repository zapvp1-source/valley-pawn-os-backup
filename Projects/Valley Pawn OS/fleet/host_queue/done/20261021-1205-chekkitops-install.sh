#!/bin/bash
# install chekkit-reviews-owed (19:05) + chekkit-assign-stale (every 5 min), then one live run of each
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/install_agent.sh" com.valleypawn.chekkit-reviews-owed
bash "$BIN/install_agent.sh" com.valleypawn.chekkit-assign-stale
python3 "$BIN/chekkit_ops.py" reviews-owed
python3 "$BIN/chekkit_ops.py" assign-stale
python3 "$BIN/texting_scorecard.py"
