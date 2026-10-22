#!/bin/bash
# Nov 1 monthly rehearsal — disarm the publish guard and confirm.
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_dryrun.py" off
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_dryrun.py" status
echo "status_rc=$?"
