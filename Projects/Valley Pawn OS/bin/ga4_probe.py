#!/usr/bin/env python3
"""ga4_probe.py OUT.json — read-only GA4 traffic-quality probe by city (added 2026-10-21 for the bot-traffic filter decision)."""
import json, os, sys
sys.path.insert(0, os.path.expanduser("~/Documents/Claude/Projects/Website/analytics/bin"))
import ga4_pull as G
R = lambda body: G.run_report(body)
s, e = "2026-07-22", "2026-10-20"
def rows(r): return [[c["value"] for c in x["dimensionValues"]] + [c["value"] for c in x["metricValues"]] for x in r.get("rows", [])]
out = {}
out["city_quality"] = rows(R({"dateRanges": [{"startDate": s, "endDate": e}], "dimensions": [{"name": "city"}],
    "metrics": [{"name": n} for n in ("sessions", "engagedSessions", "averageSessionDuration", "screenPageViewsPerSession", "keyEvents")], "limit": 25}))
out["city_events"] = rows(R({"dateRanges": [{"startDate": s, "endDate": e}], "dimensions": [{"name": "city"}, {"name": "eventName"}],
    "metrics": [{"name": "eventCount"}], "limit": 60,
    "dimensionFilter": {"andGroup": {"expressions": [
        {"filter": {"fieldName": "city", "inListFilter": {"values": ["Ashburn", "(not set)", "Moses Lake", "Boardman", "Council Bluffs", "The Dalles", "Columbus", "San Jose", "Atlanta", "Baltimore"]}}},
        {"filter": {"fieldName": "eventName", "inListFilter": {"values": ["phone_click", "sms_click", "directions_click", "Textchat Message", "Textchat Opened"]}}}]}}}))
out["ashburn_browser"] = rows(R({"dateRanges": [{"startDate": s, "endDate": e}], "dimensions": [{"name": "browser"}, {"name": "deviceCategory"}, {"name": "sessionSource"}],
    "metrics": [{"name": "sessions"}, {"name": "engagedSessions"}], "limit": 15,
    "dimensionFilter": {"filter": {"fieldName": "city", "stringFilter": {"value": "Ashburn"}}}}))
json.dump(out, open(sys.argv[1], "w"), indent=1); print("ok")
