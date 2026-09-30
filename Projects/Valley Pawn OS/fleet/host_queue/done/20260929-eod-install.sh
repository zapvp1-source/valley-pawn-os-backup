#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/install_agent.sh" com.valleypawn.eod-photo-fetch
python3 "$BIN/install_skill_block.py" jewelry-onhand-nightly-pull "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/skill_blocks/jewelry_eod_photos.md" --apply
python3 "$BIN/install_skill_block.py" jewelry-onhand-catchup "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/skill_blocks/jewelry_eod_photos.md" --apply
