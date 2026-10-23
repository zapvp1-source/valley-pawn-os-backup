#!/bin/bash
for D in 2026-10-01 2026-10-02 2026-10-03 2026-10-10; do echo "##### $D"; /usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/fleet_scorecard.py" --render $D --detail; done
