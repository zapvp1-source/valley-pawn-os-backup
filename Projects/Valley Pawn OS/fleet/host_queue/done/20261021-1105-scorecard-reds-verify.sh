#!/bin/bash
# 2026-10-21 scorecard reds: verify fixes. eBay channel audit RENDER only (read-only eBay GETs, nothing posted); scorecard renders (no send).
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/fleet_scorecard.py" --render 2026-10-19 --detail
python3 "$BIN/fleet_scorecard.py" --render 2026-10-20 --detail
python3 "$BIN/ebay_channel_audit.py" --render
bash "$BIN/tail_any.sh" ebay-weekly-channel-audit.log 30
