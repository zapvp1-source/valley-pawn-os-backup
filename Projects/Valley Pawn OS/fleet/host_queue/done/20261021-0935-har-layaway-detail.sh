#!/bin/bash
# 2026-10-21 Joshua ask: accurate Harrisonburg layaway picture. New additive read-only cell layaway-detail
# (reports/LayawayDetail.ahk). Validate + restart watcher, then pull HAR. (Session reverts file if invalid.)
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_watcher_validate.sh" --restart
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" layaway-detail 2026-10-21 HAR layaway-detail-2026-10-21-HAR
