# 75-day past-due loan list (every loan 75+ days late, all 5 stores) for the Oct 2026 rule-change outreach.
# Step 1: restart the VM watcher so it loads the new additive cell loans75-detail (reports/Loans75Detail.ahk).
# Step 2: run the saved "75 Days Past Due" report with full row capture on all 5 stores.
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_watcher_restart.sh"
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" loans75-detail saved CUL,HAR,LEX,ROA,WAY loans75-detail-2026-09-30
