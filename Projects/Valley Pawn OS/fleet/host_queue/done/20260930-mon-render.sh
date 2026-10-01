#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$HOME/Documents/Claude/Projects/Bravo Data Extraction/bin/format_aged_inventory.py" --pipeline-date 2026-09-27 --post-date 2026-09-28
python3 "$BIN/comms_engine.py" render --pub loan-review --pipeline-date 2026-09-27 --post-date 2026-09-28
python3 "$BIN/comms_engine.py" render --pub layaway-review --pipeline-date 2026-09-27 --post-date 2026-09-28
python3 "$BIN/comms_engine.py" render --pub first-payment-default --pipeline-date 2026-09-27 --post-date 2026-09-28
