#!/bin/bash
# Isolation self-test for the measurability chain (2026-09-18). Publishes NOTHING.
#   1. vp_receipt.py write/last  — the receipt primitive round-trips
#   2. vp_audit.py               — read-only; proves the 4 bonus entries now score
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== 1. receipt primitive ====="
python3 "$BIN/vp_receipt.py" write receipt-selftest --surface slack-dm --target D03BHQH5VGT --note "isolation self-test, nothing was sent"
python3 "$BIN/vp_receipt.py" last receipt-selftest
echo "===== 2. audit (read-only, no posting) ====="
python3 "$BIN/vp_audit.py" --days 60
