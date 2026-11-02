#!/bin/bash
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bonus_close_pull.py" 2026-10 --no-pull
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" bonus-month-close-pull.log 5
