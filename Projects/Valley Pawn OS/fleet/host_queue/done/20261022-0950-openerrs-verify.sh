#!/bin/bash
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/asset_recovery_native.py" snapshot
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/oura_import.sh"
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/oura_import.sh"
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" oura-daily-import.log 12
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/log_triage.py" --days 7
