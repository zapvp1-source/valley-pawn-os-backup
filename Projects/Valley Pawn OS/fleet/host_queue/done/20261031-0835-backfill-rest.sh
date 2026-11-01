#!/bin/bash
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/daily_report.sh" sold 2026-10-27
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/daily_report.sh" pawn 2026-10-28
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/daily_report.sh" discount 2026-10-28
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/funds_verification.sh" 2026-10-28
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/funds_verification.sh" 2026-10-29
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/funds_verification.sh" 2026-10-30
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" daily-funds-verification.log 30
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" jewelry-onhand-catchup.log 25
