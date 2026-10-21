#!/bin/bash
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_signin_close.sh"
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/cloudcover_check.py" --render --diag
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/clockin_check.py" --render --diag
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/northwest_check.py" --render --diag
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/dress_code_check.py" --render --diag
