#!/bin/bash
# Quota-safe photo upscale/enhance runner (replaces the old two-pass design).
# Primary-only + pre-flight quota gate + auto-stop-on-limit + clean resume.
# Safe to run daily on the scheduler: it skips items already upscaled and stops
# gracefully when eBay's daily call budget runs low, resuming the next day.
cd "/Users/joshuadavis/Documents/Claude/Projects/eBay"
LOG="$HOME/enhance_run.log"
echo "=== RUN $(date) ===" >> "$LOG"
# don't start if a run is already going
if pgrep -f 'ebay_photo_enhance.py' > /dev/null; then echo 'already running; abort' | tee -a "$LOG"; exit 0; fi
for S in Lexington Waynesboro Harrisonburg Roanoke Culpeper; do
  echo "=== $S $(date) ===" | tee -a "$LOG"
  /usr/bin/python3 ebay_photo_enhance.py "$S" "${S}_photos.json" --apply --primary-only --force --skip-upscaled --min-budget 300 2>&1 | tee -a "$LOG"
  sleep 5
done
echo RUN_COMPLETE | tee -a "$LOG"

