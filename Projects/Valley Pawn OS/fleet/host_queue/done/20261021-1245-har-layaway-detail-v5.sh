#!/bin/bash
# 2026-10-21 layaway-detail v5 (grid copy + full Down walk for balances + custom report copy). Validate + restart watcher, then pull HAR.
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_watcher_validate.sh" --restart
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" layaway-detail 2026-10-21 HAR layaway-detail-2026-10-21-HAR-v5
