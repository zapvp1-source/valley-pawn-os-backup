#!/bin/bash
cd "/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media" || exit 1
rm -f /tmp/vp_verify_0831.log
/usr/bin/python3 -u _verify_deal_reels_20260831.py > /tmp/vp_verify_0831.log 2>&1
echo "EXIT=$?" >> /tmp/vp_verify_0831.log
echo "DONE" >> /tmp/vp_verify_0831.log
