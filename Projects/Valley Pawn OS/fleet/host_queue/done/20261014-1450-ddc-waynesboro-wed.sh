#!/bin/bash
# daily-dress-code-check: add Waynesboro to the Wednesday check (Joshua 2026-10-14, Waynesboro now open 6 days).
# update_scheduled_task refused ("file is hard-linked"); install_skill.sh is the sanctioned host-side path (backs up first).
echo ===== BEFORE
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/inspect_path.py" "/Users/joshuadavis/Documents/Claude/Scheduled/daily-dress-code-check" --lines 6
echo ===== INSTALL
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_skill.sh" daily-dress-code-check "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/skill_sources/daily-dress-code-check.SKILL.md"
echo ===== AFTER
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/grep_skill.py" daily-dress-code-check Wednesdays
