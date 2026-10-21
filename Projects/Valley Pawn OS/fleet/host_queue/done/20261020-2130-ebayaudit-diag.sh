#!/bin/bash
# eBay full audit 2026-10-20 — read-only diagnostics: why no Channel Pulse post Mon 10/19
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/host_diag.sh" logs ebay-weekly-channel-audit 80
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/host_diag.sh" logs weekly-online-store-audit 40
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/host_diag.sh" logs ebay-ship-alert 40
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/host_diag.sh" agents
