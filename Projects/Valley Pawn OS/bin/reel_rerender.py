#!/usr/bin/env python3
"""reel_rerender.py <week> — re-render that week's deal reels + compilation from state/deals_<week>.json
(2026-10-05: Harrisonburg end card carried a non-existent 'Suite 22'). Writes new files only; posts untouched."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import social_weekly as sw
week = sys.argv[1]
deals = json.load(open(os.path.join(sw.RSM, "state", "deals_%s.json" % week)))
print("rendered", sw.render_reels(deals, week))
