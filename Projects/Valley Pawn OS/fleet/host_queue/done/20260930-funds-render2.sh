#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/bot_channel_check.py" C03BLHFJ3KN C03B3K5DL6T C03BLLRN64U C063K8E02TW C03BWRKEDUZ
python3 "$BIN/funds_verification.py" 2026-09-29 --render
python3 "$BIN/funds_verification.py" 2026-09-28 --render
