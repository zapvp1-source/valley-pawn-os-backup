#!/bin/bash
echo ===== CLOUDCOVER live render, unsigned profile expected
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/cloudcover_check.py" --render
echo ===== CLOUDCOVER capture render on the Mac
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/cloudcover_check.py" --render --date 2026-10-14 --from-capture "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/test_output/cloudcover_render/capture_2026-10-14T1802Z.json"
