# PM/jewelry/coin loan-growth list (Joshua 10/7). Step 1: validate + restart watcher to load additive cell pm-loan-growth.
# Step 2: probe WAY with both candidate saved reports (Loan Walk, jewelry) to confirm criteria/columns before the 5-store run.
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_watcher_validate.sh" --restart
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" pm-loan-growth walk WAY pm-loan-growth-walk-WAY-20261007
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" pm-loan-growth jewelry WAY pm-loan-growth-jewelry-WAY-20261007
