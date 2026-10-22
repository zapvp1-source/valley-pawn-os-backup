#!/bin/bash
# 2026-10-21 Nov 1 rehearsal fixes: bonus close on hr/ROSTER.json (September render) + GL watchdog local-only pass/fail tests. Render only, nothing sent.
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bonus_month_close.py" 2026-09 --render
echo "rc=$?"
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/eom_gl_watchdog.py" 2026-09 --render --state="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/test_output/gl_watchdog_test/2026-09-pass.json"
echo "rc=$?"
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/eom_gl_watchdog.py" 2026-09 --render --state="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/test_output/gl_watchdog_test/2026-09-fail.json"
echo "rc=$?"
