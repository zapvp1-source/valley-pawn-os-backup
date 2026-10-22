#!/bin/bash
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" weekly-store-perf-canvas-refresh.log 30
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" weekly-layaway-review-canvas-refresh.log 30
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" ebay-weekly-channel-audit.log 40
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" vp-comms-drift-monthly-check.log 25
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" layaway-yield-weekly.log 30
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" scrap-year-guard.log 15
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" nightly-chekkit-review-responses.out.log 15
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" review-reply.log 15
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" claude-cli-login.log 15
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" oura-daily-import.log 60
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" vsp-fee-pay.log 80
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" vsp-fee-pay.err.log 30
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" github-backup.log 10
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/quiet_triage.py" scrap-year-guard.log claude-cli-login.log nightly-chekkit-review-responses.out.log
