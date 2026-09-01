#!/bin/bash
cd "/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media" || exit 1
rm -f /tmp/vp_drift_0831.log
# One record per LIVE-VERIFIED published target (13). Engagement/reach backfilled Friday.
for ACC in Culpeper BrandIG Waynesboro BrandIG Harrisonburg BrandIG Lexington BrandIG Roanoke BrandIG Brand BrandIG BrandTikTok; do
  /usr/bin/python3 creative_drift.py record --format-id vid_deal_reel --account "$ACC" \
      --engagement 0 --reach 0 >> /tmp/vp_drift_0831.log 2>&1
  echo "recorded $ACC" >> /tmp/vp_drift_0831.log
done
echo "EXIT=$?" >> /tmp/vp_drift_0831.log
echo "DONE" >> /tmp/vp_drift_0831.log
