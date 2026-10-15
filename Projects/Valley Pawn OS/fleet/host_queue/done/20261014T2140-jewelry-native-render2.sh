#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/jewelry_nightly.py" --render --date 2026-10-13
echo "=====RENDER 10/12====="
python3 "$BIN/jewelry_nightly.py" --render --date 2026-10-12
