# Customer Loyalty report (profit contribution) for ROA + HAR — new additive cell customer-loyalty (reports/CustomerLoyalty.ahk).
# Step 1: restart the VM watcher so it loads the new handler. Step 2: pull a 5-year window (Bravo clamps the end date to yesterday).
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_watcher_restart.sh"
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" customer-loyalty "2021-09-01..2026-09-29" ROA,HAR customer-loyalty-2026-09-30
