#!/bin/bash
cd "/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media" || exit 1
rm -f /tmp/vp_publish_0831.log
/usr/bin/python3 -u vp_deal_reel_publish.py --plan manifests/deal_reels_2026-08-31.json > /tmp/vp_publish_0831.log 2>&1
echo "EXIT=$?" >> /tmp/vp_publish_0831.log
echo "DONE" >> /tmp/vp_publish_0831.log
