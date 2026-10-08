#!/bin/bash
# One-shot: backfill Jan-Jul 2025 FFL transfers (nics-transfers) for the 2025 annual count. Type A (trigger). Additive, read-only.
G="$HOME/Documents/Claude/Projects/Bravo Data Extraction/_bravo_foreground_guard.sh"
echo "guard: $(bash "$G" check)"
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" nics-transfers 2025-01-01..2025-07-31 CUL,HAR,LEX,ROA,WAY nics-2025-backfill-0107
echo exit=$?
ls -l "$HOME/Documents/Claude/Projects/Bravo Data Extraction/output/" | grep 2025-01-01
