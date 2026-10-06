#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/spot_prices.sh"
python3 "$BIN/agent_log_tail.py" vp-weekly-spot-price-update 12
python3 "$BIN/spot_site_probe.py"
