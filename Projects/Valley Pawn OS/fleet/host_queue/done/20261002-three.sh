#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/skill_dump.py" nics-monthly-ranking 14000
echo "=========== EBAY"
python3 "$BIN/skill_dump.py" monthly-ebay-ratings-sweep 12000
echo "=========== GIFT"
python3 "$BIN/skill_dump.py" monthly-gift-card-store-credit 14000
