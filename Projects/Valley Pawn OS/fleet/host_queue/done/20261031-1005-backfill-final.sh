#!/bin/bash
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" sold-discount-detail 2026-10-28..2026-10-28 HAR,LEX discount-backfill-closed-20261028
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/daily_report.sh" discount 2026-10-28
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/funds_verification.sh" 2026-10-28 --force
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/funds_verification.sh" 2026-10-29 --force
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/funds_verification.sh" 2026-10-30 --force
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" daily-funds-verification.log 12
