#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/ebay_customer_campaign.sh" --month 2026-10
bash "$BIN/tail_any.sh" ebay-customer-campaign.log 12
