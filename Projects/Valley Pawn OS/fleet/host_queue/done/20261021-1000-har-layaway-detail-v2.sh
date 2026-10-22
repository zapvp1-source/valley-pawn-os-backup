#!/bin/bash
# 2026-10-21 layaway-detail v2 (detail-panel truth walk). Validate + restart watcher, then pull HAR.
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_watcher_validate.sh" --restart
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" layaway-detail 2026-10-21 HAR layaway-detail-2026-10-21-HAR-v2
