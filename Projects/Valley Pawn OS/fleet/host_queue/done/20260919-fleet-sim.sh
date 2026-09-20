#!/bin/bash
# The sandbox suite. Builds a throwaway HOME, plants real faults, runs the REAL scripts, asserts.
# Touches nothing in production.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/fleet_sim.py"
