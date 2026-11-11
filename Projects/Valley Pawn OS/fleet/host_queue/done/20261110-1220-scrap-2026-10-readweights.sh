#!/bin/bash
# Oct 2026 scrap: zero-mutation read of all 10 October gold buckets by NAME (list reader truncates CUL/WAY)
G="/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/_bravo_foreground_guard.sh"
bash "$G" check; echo "guard=$?"
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/scrap_closeout_run.sh" scrap-2026-10-readweights 3000
