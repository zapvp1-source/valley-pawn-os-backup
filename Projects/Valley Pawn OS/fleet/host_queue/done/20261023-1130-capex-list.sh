#!/bin/bash
# Joshua 10/23: make the quarterly capex sweep work from the cloud. List the CAP GAIN tracker folders the write leg will target (read-only).
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/capex_drive_put.py" --list
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_slack.py" has C0CCH89BUNL "Dress Code" 5
