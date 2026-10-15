#!/bin/bash
set +e
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/google_regrant.sh" dry-run
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/trend_page_probe.py"
