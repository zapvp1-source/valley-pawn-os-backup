#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/comms_engine.py" results-json --pipeline-date 2026-10-04 --post-date 2026-10-05
python3 "$BIN/monday_compile.py" --render --post-date 2026-10-05
