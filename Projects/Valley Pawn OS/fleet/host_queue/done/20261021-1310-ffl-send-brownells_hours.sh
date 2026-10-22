#!/bin/bash
# HOST JOB - FFL audit 2026-10-21 execute: send brownells_hours
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/send_ffl_set.py" FFL@brownells.com "$HOME/Documents/Claude/Projects/Compliance/outbox/brownells_hours_20261021.json"
