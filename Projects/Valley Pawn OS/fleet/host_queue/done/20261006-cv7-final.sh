#!/bin/bash
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/canvas_selftest.py" delete F0C81A69N9W F0C76Q1P2FL F0C70MZ7MGB F0C7508FVDL F0C7AKEF752
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/weekly_canvases.py" loan --render --post-date 2026-10-05
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/weekly_canvases.py" layaway --render --post-date 2026-10-05
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/weekly_canvases.py" employee --render --post-date 2026-10-05
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/weekly_canvases.py" aged --render --post-date 2026-10-05
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/weekly_canvases.py" store --render --post-date 2026-10-05
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/layaway_yield_weekly.py" --render --end 2026-10-04
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/catchup.py" --render
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.loan-canvas
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.layaway-canvas
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.employee-canvas
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.aged-canvas
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.store-canvas
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.layaway-yield-weekly
