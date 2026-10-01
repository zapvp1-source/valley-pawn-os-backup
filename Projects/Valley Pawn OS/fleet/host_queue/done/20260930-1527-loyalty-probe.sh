# Discovery run for Bravo's per-customer Customer Loyalty report (no screen control). New additive cell customer-loyalty-probe.
# Step 1: restart the watcher so it loads the new handler. Step 2: probe Emmett Looney at Roanoke (the "date" field carries the name).
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_watcher_restart.sh"
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" customer-loyalty-probe "EMMETT LOONEY" ROA loyalty-probe-looney-2026-09-30
