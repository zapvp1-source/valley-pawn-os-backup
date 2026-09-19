#!/bin/bash
# Apply the publish-guard precondition to all Tier-1 Cowork SKILLs (backed up, idempotent).
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/install_dryrun_check.py" --apply
echo "===== idempotency re-run (must be 0 written / 45 already) ====="
python3 "$BIN/install_dryrun_check.py"
