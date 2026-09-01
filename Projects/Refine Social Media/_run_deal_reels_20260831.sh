#!/bin/bash
cd "/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media" || exit 1
rm -f /tmp/vp_render_0831.log
/usr/bin/python3 vp_deal_reel.py --spec "_spec_deal_reels_2026-08-31.json" --outdir reels/ > /tmp/vp_render_0831.log 2>&1
echo "EXIT=$?" >> /tmp/vp_render_0831.log
echo "DONE" >> /tmp/vp_render_0831.log
