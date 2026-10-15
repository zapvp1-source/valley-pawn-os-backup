#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/canvas_migrate.py" create
python3 "$BIN/canvas_migrate.py" status
python3 "$BIN/canvas_selftest.py" delete F0C8M2TECJE F0C8P5YEUBB F0C8F11R84T F0C8K8V3ZP0 F0C8K8VFSLE
python3 "$BIN/weekly_canvases.py" loan --render --post-date 2026-10-12
python3 "$BIN/weekly_canvases.py" layaway --render --post-date 2026-10-12
python3 "$BIN/weekly_canvases.py" employee --render --post-date 2026-10-12
python3 "$BIN/weekly_canvases.py" aged --render --post-date 2026-10-12
python3 "$BIN/weekly_canvases.py" store --render --post-date 2026-10-12
python3 "$BIN/layaway_yield_weekly.py" --render
