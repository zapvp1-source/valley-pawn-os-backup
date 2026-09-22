#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== render ====="
bash "$BIN/mail_brief.sh" --render
echo "===== install 18:00 daily ====="
bash "$BIN/install_agent.sh" com.valleypawn.mail-brief
echo "===== usearch root-cause probe (was queued) ====="
python3 "$BIN/usearch_scan_probe.py"
