#!/bin/bash
# HOST JOB — Roanoke Wednesdays r3: patch the 5 suspended campaigns the r2 run lost to Brevo 429s, re-sync the
# Roanoke list (r2 showed 591 of 891), build announcement + preflight + test to jdavis@. NOT scheduled here.
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/roanoke_wed_brevo.py" --patch-ids 51,40,18,17,16 --roanoke-list --build --lists roanoke
