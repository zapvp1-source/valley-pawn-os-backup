#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
/usr/bin/python3 "$BIN/comms_engine.py" retract --channel C0B8WR95N31 --ts 1789659030.578769
/usr/bin/python3 "$BIN/vp_slack.py" last C0B8WR95N31 4
