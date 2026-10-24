#!/bin/bash
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.py" "/Users/joshuadavis/Library/Logs/valleypawn/email-analytics-weekly.log" --lines 20
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.py" "/Users/joshuadavis/Library/Logs/valleypawn/brevo-preflight-watchdog.log" --lines 10
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.py" "/Users/joshuadavis/Library/Logs/valleypawn/vp-publer-analytics-friday.log" --lines 10
