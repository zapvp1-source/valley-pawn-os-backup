#!/bin/bash
cd "/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media" || exit 1
rm -f /tmp/vp_compil_0831.log
/usr/bin/python3 vp_deal_compilation.py --reels reels/ --out reels/publish/ > /tmp/vp_compil_0831.log 2>&1
echo "EXIT=$?" >> /tmp/vp_compil_0831.log
echo "DONE" >> /tmp/vp_compil_0831.log
