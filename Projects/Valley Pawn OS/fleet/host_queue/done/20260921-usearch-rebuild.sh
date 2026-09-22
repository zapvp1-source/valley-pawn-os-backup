#!/bin/bash
# FDA appears to have landed (tmutil answered today, failed yesterday). Prove it on the two
# surfaces that were actually denied — Mail and Messages — by re-running the real rebuild now
# instead of waiting for 04:50 tomorrow. The shrink guard protects the index either way.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/usearch_refresh.sh"
