#!/bin/bash
# 2026-10-21 Joshua: all Valley Pawn files in jdavis@fcfpawn.com. Create the jdavis copy of "Valley Pawn Trends" from the 10/21 Chrome extract, verify cell by cell, then a render-only gun-audit sheet test. Original sheet untouched. No Slack.
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/trends_migrate.py"
python3 "$BIN/trends_migrate.py" --live
python3 "$BIN/trends_migrate.py" --sheet-test 2026-09
