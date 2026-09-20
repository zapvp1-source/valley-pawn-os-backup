#!/bin/bash
# Live run: proves the compliance brief can finally reach Joshua (it never could before).
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/compliance_brief.py"
echo "===== receipt proof ====="
python3 "$BIN/vp_receipt.py" last compliance-brief
