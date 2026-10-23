#!/bin/bash
echo ===== dry run
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/ask_vp_invite_staff.py"
echo ===== apply
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/ask_vp_invite_staff.py" --apply
