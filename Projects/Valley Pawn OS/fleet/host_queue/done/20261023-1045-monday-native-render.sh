#!/bin/bash
# Joshua 10/23: make native monday-compile the Monday driver. Prove it renders every Monday post (print only, nothing sent).
echo ===== RENDER 2026-10-19
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/monday_compile.py" --render --pipeline-date 2026-10-19 --post-date 2026-10-19
echo ===== DONE
