#!/bin/bash
# Install the community share auto-post agent (Joshua 2026-11-02: "split version"). Render first; RunAtLoad fires the first live run.
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/community_share_autopost.py" --render
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.community-share-autopost
sleep 60
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" "/Users/joshuadavis/Library/Logs/valleypawn/community-share-autopost.log"
