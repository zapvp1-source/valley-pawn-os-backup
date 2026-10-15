#!/bin/bash
echo ===== EBAY replay 9/07 on the Mac
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/ebay_channel_audit.py" --render --as-of 2026-09-07 --from "/Users/joshuadavis/Documents/Claude/Projects/eBay/audit_weekly/2026-09-07"
echo ===== EBAY live render today
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/ebay_channel_audit.py" --render
