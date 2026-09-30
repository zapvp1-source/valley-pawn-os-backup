#!/bin/bash
# HOST JOB — nics-weekly-mtd-ranking backfill for the missed 2026-09-28 run (v2: one plain command per line).
# WAY + HAR already on disk for 2026-09-01..2026-09-28. Single-store sequential pulls (pattern proven 9/21).
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" nics-transfers "2026-09-01..2026-09-28" CUL nics-mtd-backfill-20260929-CUL
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" nics-transfers "2026-09-01..2026-09-28" LEX nics-mtd-backfill-20260929-LEX
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" nics-transfers "2026-09-01..2026-09-28" ROA nics-mtd-backfill-20260929-ROA
