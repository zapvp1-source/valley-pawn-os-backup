#!/bin/bash
# Fleet Guardian 2026-10-21 ~16:47 UTC pass: registry snapshot for missed-run detection.
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/task_preflight.py"
echo "---REG_SHAPE---"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/reg_shape.py"
