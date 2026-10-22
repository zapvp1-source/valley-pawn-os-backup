#!/bin/bash
# Records Admin audit 2026-10-21: vp-hiring-pipeline DMs Joshua "nothing new to action" every 15 min (~25/day) despite its own "post nothing if nothing changed" rule. Append an explicit quiet block (additive, backed up, idempotent).
echo ===== BEFORE
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/skill_dump.py" vp-hiring-pipeline 6000
echo ===== APPLY
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_skill_block.py" vp-hiring-pipeline "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/skill_sources/vp-hiring-pipeline.quiet-block.md" --apply
echo ===== AFTER
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/grep_skill.py" vp-hiring-pipeline "QUIET RULE"
