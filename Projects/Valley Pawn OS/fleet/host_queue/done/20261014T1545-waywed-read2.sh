#!/bin/bash
# Waynesboro Wednesday — read exact Wednesday sentences (read-only).
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/grep_skill.py" daily-clockin-check "Wednesdays:** Culpeper and Roanoke"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/grep_skill.py" daily-clockin-check "Format (Wednesday"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/grep_skill.py" daily-clockin-check "Wednesday = Culpeper + Roanoke only"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/grep_skill.py" jewelry-onhand-nightly-pull "Wednesday -> [\"CUL\",\"ROA\"]"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/grep_skill.py" jewelry-onhand-catchup "Wednesday"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/grep_skill.py" daily-cloudcover-check "IMPORTANT — Wednesday rule"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/grep_skill.py" daily-cloudcover-check "FRIENDLY_NAMES = { 'SandiPepper': 'Culpeper', 'Roanoke1'"
