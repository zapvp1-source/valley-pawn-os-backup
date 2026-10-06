#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/website_deals.py"
bash "$BIN/install_agent.sh" com.valleypawn.website-deals
