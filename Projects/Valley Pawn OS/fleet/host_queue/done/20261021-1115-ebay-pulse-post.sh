#!/bin/bash
# 2026-10-21: post this week's overdue eBay Channel Pulse ONCE, from the verified 11:01-11:05 read-only pull (all 5 stores, 0 store errors). Script's own has-check prevents a second post.
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/ebay_channel_audit.py" --send --from "/Users/joshuadavis/Documents/Claude/Projects/eBay/audit_weekly/2026-10-21"
bash "$BIN/tail_any.sh" ebay-weekly-channel-audit.log 6
