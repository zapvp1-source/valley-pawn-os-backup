#!/bin/bash
# Mutation testing: re-introduce each fixed bug into a COPY of bin/ and confirm the suite catches it.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/fleet_sim.py" --mutate
