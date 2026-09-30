#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/install_agent.sh" com.valleypawn.ebay-ship-alert
bash "$BIN/host_diag.sh" agents
