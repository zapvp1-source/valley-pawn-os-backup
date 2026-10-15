#!/bin/bash
set +e
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/website_trend_refresh.py" --render
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/inspect_path.py" "$HOME/Documents/Claude/Artifacts" "$HOME/Documents/Claude/Artifacts/vp-website-trend"
