#!/bin/bash
OS="$HOME/Documents/Claude/Projects/Valley Pawn OS"
python3 "$OS/bin/ask_vp_corpus.py" --force
python3 "$OS/bin/ask_vp_responder.py" --selftest
