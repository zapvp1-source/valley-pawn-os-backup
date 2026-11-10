#!/bin/bash
OS="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS"
bash "$OS/bin/local_ai_engine.sh" ensure
python3 "$OS/bin/vp_ai.py" --selftest --local
python3 "$OS/bin/continuity_selftest.py" --quiet-ledger
