#!/bin/bash
# HOST JOB - read-only: newest MasterFFL sign-in code to roanoke@ (FFL audit hours fix 2026-10-21)
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/mail_latest_body.py" masterffl --to roanoke --hours 1
