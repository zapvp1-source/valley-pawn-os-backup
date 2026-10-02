#!/bin/bash
# HOST JOB — Roanoke now open Wednesdays (Joshua 2026-10-01): patch T11/T48 + unsent campaigns (backups first),
# build Roanoke list from STORE=Roanoke, build announcement campaign (master T48), preflight, test to jdavis@. NOT scheduled here.
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/roanoke_wed_brevo.py" --patch --roanoke-list --lists-info --build --lists roanoke
