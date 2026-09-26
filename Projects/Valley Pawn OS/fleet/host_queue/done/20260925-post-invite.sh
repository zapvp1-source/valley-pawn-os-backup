#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/bot_channel_check.py" C04TXF0KGNL C0ANVN5KX4Y C0APR5WUL2Z C0APY6TE604 C0ASE9C0GQ0 C0AVCANK7E3 C0B0FQZ4FS8 C0BHTEUPADB C0BMRC2LN3D C0BP4M3B99R
bash "$BIN/email_analytics_weekly.sh"
bash "$BIN/install_agent.sh" com.valleypawn.zoom-missed-alert --restart-only
