#!/usr/bin/env python3
"""ga4_sms_today.py -- READ-ONLY GA4 report (2026-11-19): today's website visits that came from the text
(utm_source=sms), by landing page, plus the events and outbound clicks (app-store links) in those sessions.
Writes fleet/state/ga4_sms_today.json."""
import json, os, sys
sys.path.insert(0, os.path.expanduser("~/Documents/Claude/Projects/Website/analytics/bin"))
import ga4_pull as G
D = [{"startDate": "today", "endDate": "today"}]
F = {"filter": {"fieldName": "sessionSource", "stringFilter": {"value": "sms"}}}
def rows(r): return [[c["value"] for c in x.get("dimensionValues", [])] + [c["value"] for c in x.get("metricValues", [])] for x in r.get("rows", [])]
out = {}
def rep(name, dims, mets, flt=F, limit=40):
    try:
        out[name] = rows(G.run_report({"dateRanges": D, "dimensions": [{"name": d} for d in dims], "metrics": [{"name": m} for m in mets], "dimensionFilter": flt, "limit": limit}))
    except Exception as e:
        out[name] = "ERR " + str(e)[:200]
rep("total", [], ["sessions", "totalUsers", "engagedSessions"])
rep("landing", ["landingPage"], ["sessions", "totalUsers"])
rep("device", ["deviceCategory", "operatingSystem"], ["sessions"])
rep("events", ["eventName"], ["eventCount", "totalUsers"])
rep("outbound", ["linkUrl"], ["eventCount", "totalUsers"])
rep("hour", ["hour"], ["sessions"])
rep("app_page_all_sources", ["sessionSource"], ["sessions", "totalUsers"], {"filter": {"fieldName": "pagePath", "stringFilter": {"matchType": "BEGINS_WITH", "value": "/app"}}})
json.dump(out, open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fleet", "state", "ga4_sms_today.json"), "w"), indent=1)
print(json.dumps(out)[:3000])
