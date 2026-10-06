#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/install_skill_block.py" vp-ai-search-health-check "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/skill_blocks/harrisonburg_suite22.md" --apply
python3 "$BIN/install_skill_block.py" vp-presence-audit-weekly "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/skill_blocks/harrisonburg_suite22.md" --apply
python3 "$BIN/install_skill_block.py" vp-ai-search-autofix "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/skill_blocks/harrisonburg_suite22.md" --apply
python3 "$BIN/install_skill_block.py" vp-ai-visibility-metrics "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/skill_blocks/harrisonburg_suite22.md" --apply
