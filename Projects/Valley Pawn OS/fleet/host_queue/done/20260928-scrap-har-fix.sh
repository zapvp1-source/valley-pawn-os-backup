# Final 3 August gold buckets: HAR's true bucket names are "2026-08 GOLD" /
# "2026-08 GOLD WITH STONES" (same convention as the other 4 stores) - the
# original manifest's legacy names ("GOLD W/O STONES"/"GOLD W STONES") never
# matched anything live, which is why HAR failed both prior passes. Confirmed
# via the all-status inventory (scrap-har-allstatus-list). ROA WITH STONES
# retried with the numeric-tolerance verify fix (0.44 vs 0.440 false failure).
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/scrap_closeout_run.sh" scrap-closeout-2026-08-live-har-fix 1500
