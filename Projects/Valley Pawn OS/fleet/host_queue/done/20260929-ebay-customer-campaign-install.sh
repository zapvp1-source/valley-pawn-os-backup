#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/install_agent.sh" com.valleypawn.ebay-customer-campaign
bash "$BIN/ebay_customer_campaign.sh" --month 2026-10
bash "$BIN/host_diag.sh" agents
