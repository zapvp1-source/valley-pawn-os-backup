#!/bin/bash
# Apply the receipt step to the 11 receipt-scored SKILL.md files (backed up, idempotent).
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/install_receipt_step.py" --apply
echo "===== idempotency re-run (must report 11 already had it, 0 written) ====="
python3 "$BIN/install_receipt_step.py"
