#!/usr/bin/env python3
"""gsc_store_history.py — read-only. Monthly Search Console per store (Jun 2025 → last full data),
for the aggregator-expiry question (2026-10-21). Writes data/gsc/store_history.json."""
import sys, json, datetime as dt
from pathlib import Path
HERE = Path(__file__).resolve().parents[2] / "Website" / "analytics" / "bin"
sys.path.insert(0, str(HERE))
import gsc_pull as g
cities = ["culpeper", "waynesboro", "harrisonburg", "lexington", "roanoke"]
last = dt.date.today() - dt.timedelta(days=3)
d = dt.date(2025, 6, 1); out = {}
while d <= last:
    nxt = (d.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    e = min(nxt - dt.timedelta(days=1), last)
    qrows = g.query(str(d), str(e), ["query"], limit=25000)
    prows = g.query(str(d), str(e), ["page"], limit=25000)
    tot = g.query(str(d), str(e), [])
    m = {"_days": (e - d).days + 1,
         "_site": [int(tot[0]["impressions"]), int(tot[0]["clicks"])] if tot else [0, 0]}
    for c in cities:
        gen = [r for r in qrows if c in r["keys"][0].lower() and "valley" not in r["keys"][0].lower()]
        brand = [r for r in qrows if c in r["keys"][0].lower() and "valley" in r["keys"][0].lower()]
        pg = [r for r in prows if c in r["keys"][0].lower()]
        m[c] = {"generic_imp": int(sum(r["impressions"] for r in gen)), "generic_clk": int(sum(r["clicks"] for r in gen)),
                "brand_imp": int(sum(r["impressions"] for r in brand)), "brand_clk": int(sum(r["clicks"] for r in brand)),
                "pages_imp": int(sum(r["impressions"] for r in pg)), "pages_clk": int(sum(r["clicks"] for r in pg))}
    out[str(d)[:7]] = m
    print(str(d)[:7], json.dumps(m), flush=True)
    d = nxt
(HERE.parent / "data" / "gsc" / "store_history.json").write_text(json.dumps(out, indent=1))
print("WROTE store_history.json")
