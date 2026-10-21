#!/bin/bash
# eBay full audit 2026-10-20 — read-only inspection of home-folder eBay scripts/state
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/inspect_path.py" ~/ebay_weekly_rankings.py ~/ebay_policy_fix_state.json ~/ebay_markdown_state.json ~/.vp_secrets --lines 60
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/inspect_path.py" ~/ebay_daily_listings.py ~/ebay_efficiency_weekly.py ~/vp_weekly_online_store_audit.py ~/ebay_markdown_engine.py --lines 30
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/host_diag.sh" logs ebay-daily-listings 20
