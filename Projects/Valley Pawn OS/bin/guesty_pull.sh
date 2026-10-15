#!/bin/bash
AGENT=guesty-pull; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; vp_lock guesty-pull 30
vlog "$(/usr/bin/python3 "$BIN/guesty_pull.py" 2>&1 | tail -1)"
