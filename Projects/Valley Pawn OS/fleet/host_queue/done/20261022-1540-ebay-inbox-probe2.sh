#!/bin/bash
echo ===== PROBE raw headers
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/ebay_inbox_alert.py" --probe
echo ===== RENDER am slot
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/ebay_inbox_alert.py" --slot am --render
