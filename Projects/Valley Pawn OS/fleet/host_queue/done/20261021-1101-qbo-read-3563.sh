#!/bin/bash
# read-only: WF 3563 and Bravo POS Clearing ledgers since 9/1, Classes list
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" gl "WF Checking 3563" 2026-09-01 2026-10-21 gl_3563_sepoct
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" gl "Bravo POS Clearing" 2026-09-01 2026-10-21 gl_bpc_sepoct
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" gl "WF Checking 2797" 2026-09-15 2026-10-21 gl_2797_late
