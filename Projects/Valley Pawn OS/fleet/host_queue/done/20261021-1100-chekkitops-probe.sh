#!/bin/bash
# chekkit_ops probe + renders (read-only, changes nothing in Chekkit)
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/chekkit_ops.py" probe
python3 "$BIN/chekkit_ops.py" reviews-owed --render
python3 "$BIN/chekkit_ops.py" assign-stale --render
