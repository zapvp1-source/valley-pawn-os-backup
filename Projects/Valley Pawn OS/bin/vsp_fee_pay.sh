#!/bin/bash
# launchd wrapper — com.valleypawn.vsp-fee-pay, 5th of month 10:15 (native, 2026-10-20).
# Default mode is --read (balances + one DM). Switch to --pay once Joshua has stored the ACH details in Keychain
# and said go: edit the MODE line below (that is the only switch).
AGENT="vsp-fee-pay"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
MODE="--pay"   # 2026-10-20: Joshua stored the ACH details in Keychain and asked for hands-off; 5/5 dry run passed
vp_lock "$AGENT" 60
"$PY" "$BIN/vsp_fee_pay.py" $MODE "$@" >> "$VLOG/$AGENT.log" 2>&1
