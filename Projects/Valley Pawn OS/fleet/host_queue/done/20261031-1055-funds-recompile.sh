#!/bin/bash
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/funds_verification.sh" 2026-10-28 --force --no-pull
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/funds_verification.sh" 2026-10-29 --force --no-pull
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/funds_verification.sh" 2026-10-30 --force --no-pull
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" daily-funds-verification.log 6
