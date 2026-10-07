#!/bin/bash
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/weekly_canvases.py" loan --render --post-date 2026-10-05
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/weekly_canvases.py" loan --render --post-date 2026-08-31 --pipeline-date 2026-08-30
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/weekly_canvases.py" layaway --render --post-date 2026-10-05
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/weekly_canvases.py" employee --render --post-date 2026-10-05
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/weekly_canvases.py" aged --render --post-date 2026-10-05
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/weekly_canvases.py" store --render --post-date 2026-09-28 --end 2026-09-27
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/weekly_canvases.py" store --render --post-date 2026-10-05
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/layaway_yield_weekly.py" --render --end 2026-10-04
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/canvas_selftest.py" create --post-date 2026-10-05
