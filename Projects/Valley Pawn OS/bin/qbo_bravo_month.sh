#!/bin/bash
# qbo_bravo_month.sh YYYY-MM [--go] — runs Quickbooks Set UP/post_bravo_month.py (monthly BRAVO-<ST>-YYYY-MM entries) from its own folder. 2026-10-21.
cd "$HOME/Documents/Claude/Projects/Quickbooks Set UP" || exit 2
/usr/bin/python3 post_bravo_month.py "$@"
