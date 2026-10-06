#!/bin/bash
echo ===== canvas probe
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/canvas_scope_probe.py"
echo ===== md review render
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/markdown_verification.py" review --render
echo ===== md pull render
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/markdown_verification.py" pull --render
echo ===== bonus pace render
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/bonus_pace.py" --render
