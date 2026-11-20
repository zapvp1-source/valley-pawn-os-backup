#!/usr/bin/env python3
"""sync_shadow.py [order_days] — READ-ONLY rehearsal of both sync directions. Sends nothing.
eBay calls used (reads only): GetMyeBaySelling, GetOrders. Bravo: reads sold CSVs already on disk.
Writes out/sync_shadow_<tag>.json: takedown plan, ring plan, and a stale-listing audit
(live on eBay but Bravo already shows the item sold in the last 60 days, not through eBay)."""
import glob, json, os, sys, time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import ebay_common as ec
import desk_core as dc
import desk_sync as ds
READS = ("GetMyeBaySelling", "GetOrders")
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 3
NOW = datetime.now(timezone.utc); TODAY = (NOW - timedelta(hours=5)).date()
SOLD_DIR = os.path.join(HERE, "..", "..", "Bravo Data Extraction", "output")
t0 = time.time()
active = {s: ec.active_items(ec.token_for(s)) for s in ec.STORE_ORDER}
t_active = time.time() - t0
lines = []
for s in ec.STORE_ORDER:
    page = 1
    while True:
        r = ec.call(ec.token_for(s), "GetOrders", "<CreateTimeFrom>%s</CreateTimeFrom><CreateTimeTo>%s</CreateTimeTo><OrderRole>Seller</OrderRole>"
                    "<OrderStatus>All</OrderStatus><Pagination><EntriesPerPage>100</EntriesPerPage><PageNumber>%d</PageNumber></Pagination>"
                    % ((NOW - timedelta(days=max(DAYS, 60))).strftime("%Y-%m-%dT%H:%M:%S.000Z"), NOW.strftime("%Y-%m-%dT%H:%M:%S.000Z"), page))
        if not ec.ack_ok(r): raise RuntimeError(ec.errors(r)[:1])
        lines += dc.parse_get_orders(ET.tostring(r, encoding="unicode"), s)
        if (r.findtext("{%s}HasMoreOrders" % ec.NS) or "false").lower() != "true": break
        page += 1
t_orders = time.time() - t0 - t_active
def sold_since(days):
    files = [f for f in glob.glob(os.path.join(SOLD_DIR, "*_sold-discount-detail.csv"))
             if os.path.basename(f)[:10] >= str(TODAY - timedelta(days=days))]
    return dc.load_bravo_sold(files), len(files)
idx, dup = ds.live_index(active)
ebay_codes = [l["bravo_no"] for l in lines if l["bravo_no"]]
sold2, nf2 = sold_since(2)
take = ds.takedown_plan(idx, sold2, ebay_codes, TODAY)
sold60, nf60 = sold_since(60)
stale = [dict(bravo_no=c, store=idx[c][0], item_id=idx[c][1], title=idx[c][2], bravo_sold=str(h["date"]), bravo_price=h["price"])
         for c, h in sorted(sold60.items()) if c in idx and c not in set(ebay_codes)]
recent = [l for l in lines if datetime.fromisoformat(l["paid_utc"]) >= NOW - timedelta(days=DAYS)]
ring = ds.ring_plan(recent, sold60)
from collections import Counter
res = {"run_utc": NOW.isoformat(), "live_listings": {s: len(v) for s, v in active.items()}, "live_with_bravo_no": len(idx), "duplicate_numbers": dup,
       "seconds": {"active_listings": round(t_active, 1), "orders": round(t_orders, 1)},
       "takedown": take, "stale_live_listings": stale, "ring": ring, "ring_counts": dict(Counter(r["action"] for r in ring)),
       "sold_files_2d": nf2, "sold_files_60d": nf60}
dst = os.path.join(HERE, "out", "sync_shadow_%s.json" % time.strftime("%Y-%m-%d_%H%M"))
json.dump(res, open(dst, "w"), indent=1, default=str)
print(json.dumps({k: res[k] for k in ("live_listings", "live_with_bravo_no", "duplicate_numbers", "seconds", "ring_counts", "sold_files_2d", "sold_files_60d")}))
print("takedown now:", len(take["end"]), take["halt"]); [print("  END", e["store"], e["item_id"], e["bravo_no"], e["sold_in_store"], e["title"][:50]) for e in take["end"]]
print("stale live listings (Bravo sold <=60d, not via eBay):", len(stale)); [print("  ", x["store"], x["item_id"], x["bravo_no"], x["bravo_sold"], x["bravo_price"], x["title"][:45]) for x in stale]
for r in ring:
    if r["action"] != "verified": print("  RING?", r["action"], r["store"], r.get("bravo_no"), r["ring_price"], r["paid_utc"][:16], r.get("why", ""))
print("->", dst)
