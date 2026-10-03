#!/bin/bash
# copy_parse_eom.sh — vendor the verified parse_eom.py (Scheduled/monthly-analytics-report) into Valley Pawn OS/bin
# so native agents can use it; the original stays where it is (Rule 4, additive).
S="$HOME/Documents/Claude/Scheduled/monthly-analytics-report/parse_eom.py"
D="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/parse_eom.py"
cmp -s "$S" "$D" 2>/dev/null && echo "already identical" || { cp "$S" "$D" && echo "copied $(wc -l < "$D") lines"; }
