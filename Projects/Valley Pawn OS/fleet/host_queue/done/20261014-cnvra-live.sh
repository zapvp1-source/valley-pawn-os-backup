#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/weekly_canvases.py" loan --post-date 2026-10-12
python3 "$BIN/weekly_canvases.py" layaway --post-date 2026-10-12
python3 "$BIN/weekly_canvases.py" employee --post-date 2026-10-12
python3 "$BIN/weekly_canvases.py" aged --post-date 2026-10-12
python3 "$BIN/weekly_canvases.py" store --post-date 2026-10-12
python3 "$BIN/layaway_yield_weekly.py"
python3 "$BIN/canvas_migrate.py" status
