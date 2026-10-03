#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/ebay_ratings_pull.sh"
bash "$BIN/install_agent.sh" com.valleypawn.ebay-ratings-pull
python3 "$BIN/install_skill_block.py" monthly-ebay-ratings-sweep "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/skill_blocks/ebay_ratings_data_on_disk.md" --apply
