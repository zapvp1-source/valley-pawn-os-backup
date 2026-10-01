#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/install_agent.sh" com.valleypawn.funds-verification
python3 "$BIN/funds_verification.py" 2026-09-29 --no-pull
