#!/bin/bash
# email audit fixes 2026-10-20: APPLY to unsent campaigns (hours, deal map utm, weekly audience 7+10+13); backups in Email Refinement/_audit/backup_20261020_fixes/
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/email_fixes_20261020.py" --apply
python3 "$BIN/email_fixes_20261020.py" --inspect
