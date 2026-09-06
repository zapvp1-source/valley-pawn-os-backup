#!/usr/bin/env python3
"""READ-ONLY probe: can we pull eBay Seller Standards headlessly via the REST Analytics API
with the same per-store tokens the markdown engine already uses?

GetSellerDashboard (Trading) now returns 404, which is why the monthly ratings sweep has been
depending on whichever account Chrome happened to be signed into.
"""
import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError

sys.path.insert(0, os.path.expanduser("~/.vp_secrets"))

PATHS = [os.path.expanduser("~/ebay_weekly_rankings.py")]
BASE = "https://api.ebay.com/sell/analytics/v1/seller_standards_profile"


def stores():
    for p in PATHS:
        if os.path.exists(p):
            ns = {}
            exec(compile(open(p).read(), p, "exec"), ns)
            if "STORES" in ns:
                return ns["STORES"]
    raise SystemExit("no tokens")


for s in stores():
    print("=====", s["name"])
    for url in (BASE, BASE + "/program/PROGRAM_US/cycle/CURRENT"):
        try:
            r = urlopen(Request(url, headers={"Authorization": "Bearer " + s["token"],
                                              "Accept": "application/json"}), timeout=45)
            d = json.loads(r.read().decode())
            profs = d.get("standardsProfiles", [d])
            for p in profs:
                if p.get("program") in (None, "PROGRAM_US"):
                    print("  ", p.get("program"), p.get("cycle", {}).get("cycleType"),
                          "level:", p.get("standardsLevel"), "| eval:", p.get("evaluationDate"),
                          "| next:", p.get("evaluationReason"))
                    for m in p.get("metrics", []):
                        print("      ", m.get("metricKey"), m.get("value"),
                              "threshold", (m.get("thresholdLowerBound") or m.get("thresholdUpperBound")),
                              m.get("metricUnit") or "")
            break
        except HTTPError as e:
            print("  ", url.split("/v1/")[-1], "HTTP", e.code, e.read()[:160].decode(errors="replace"))
        except Exception as e:
            print("  ERROR", repr(e)[:160])
