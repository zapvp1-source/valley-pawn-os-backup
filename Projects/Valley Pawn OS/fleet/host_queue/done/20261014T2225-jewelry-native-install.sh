#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/install_agent.sh" com.valleypawn.jewelry-nightly
bash "$BIN/install_agent.sh" com.valleypawn.jewelry-catchup
echo "dormant check (must print nothing and exit 0):"
bash "$BIN/jewelry_nightly.sh"
bash "$BIN/jewelry_catchup.sh"
python3 "$BIN/catchup.py" --render
