#!/bin/bash
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.asset-recovery
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/asset_recovery_native.py" render
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/asset_recovery_native.sh"
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/inspect_path.py" "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/state/asset_recovery/render" "/Users/joshuadavis/Library/Logs/valleypawn/asset-recovery-daily-refresh.log"
