#!/bin/bash
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/chekkit_api_test.py"
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/skill_dump.py" review-obtained-last-week 30000
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/skill_dump.py" google-reviews-post-watchdog 30000
