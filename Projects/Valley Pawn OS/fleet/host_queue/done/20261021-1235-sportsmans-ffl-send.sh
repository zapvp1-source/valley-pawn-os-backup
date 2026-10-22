#!/bin/bash
# HOST JOB - send signed WAY/HAR/LEX FFL PDFs + store details to Sportsman's Warehouse (reply to their 10/2 request) - FFL audit 2026-10-21
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/send_ffl_set.py" fflorders@sportsmans.com "$HOME/Documents/Claude/Projects/Compliance/outbox/sportsmans_20261021.json"
