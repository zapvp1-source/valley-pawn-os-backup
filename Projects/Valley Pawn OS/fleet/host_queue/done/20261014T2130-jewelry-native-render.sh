#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "=====SHEETS 10/14 WAY====="
python3 "$BIN/jewelry_nightly.py" sheets --date 2026-10-14 --stores WAY
echo "=====RENDER 10/13====="
python3 "$BIN/jewelry_nightly.py" --render --date 2026-10-13
