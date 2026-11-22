#!/usr/bin/env python3
"""takedown_watch.py <sold-today-all.csv> — WATCH ONLY (eBay Desk, 2026-11-21). Ends nothing.
Reads Bravo's company-wide sold-today CSV, the live eBay listings and recent eBay orders (eBay READ calls only:
GetMyeBaySelling, GetOrders), and appends what the takedown loop WOULD end to out/takedown_watch.jsonl.
Each would-end listing is logged once (state file), with the time it was first seen."""
import json, os, sys, time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import ebay_common as ec
import desk_core as dc
import desk_sync as ds
OUT = os.path.join(HERE, "out"); LOG = os.path.join(OUT, "takedown_watch.jsonl"); STATE = os.path.join(OUT, "takedown_watch_state.json")
NOW = datetime.now(timezone.utc); TODAY = (NOW - timedelta(hours=5)).date()
csv_path = sys.argv[1]
sold = dc.load_bravo_sold([csv_path])
active = {s: ec.active_items(ec.token_for(s)) for s in ec.STORE_ORDER}
lines = []
for s in ec.STORE_ORDER:
    page = 1
    while True:
        r = ec.call(ec.token_for(s), "GetOrders", "<CreateTimeFrom>%s</CreateTimeFrom><CreateTimeTo>%s</CreateTimeTo><OrderRole>Seller</OrderRole>"
                    "<OrderStatus>All</OrderStatus><Pagination><EntriesPerPage>100</EntriesPerPage><PageNumber>%d</PageNumber></Pagination>"
                    % ((NOW - timedelta(days=14)).strftime("%Y-%m-%dT%H:%M:%S.000Z"), NOW.strftime("%Y-%m-%dT%H:%M:%S.000Z"), page))
        if not ec.ack_ok(r): raise RuntimeError("GetOrders %s %s" % (s, ec.errors(r)[:1]))
        lines += dc.parse_get_orders(ET.tostring(r, encoding="unicode"), s)
        if (r.findtext("{%s}HasMoreOrders" % ec.NS) or "false").lower() != "true": break
        page += 1
idx, dup = ds.live_index(active)
state = json.load(open(STATE)) if os.path.exists(STATE) else {}
plan = ds.takedown_plan(idx, sold, [l["bravo_no"] for l in lines if l["bravo_no"]], TODAY, already_ended=())
new = []
for e in plan["end"] + plan.get("held", []):
    k = e["item_id"]
    if k not in state:
        state[k] = {"first_seen_utc": NOW.isoformat(), "bravo_no": e["bravo_no"], "store": e["store"]}
        new.append(e)
gone = [k for k in state if k not in {i["ItemID"] for v in active.values() for i in v} and "ended_seen_utc" not in state[k]]
for k in gone: state[k]["ended_seen_utc"] = NOW.isoformat()     # a person ended it (or it sold): measures today's manual lag
rec = {"run_utc": NOW.isoformat(), "bravo_sold_rows": len(sold), "live": sum(len(v) for v in active.values()), "live_numbered": len(idx),
       "would_end_now": len(plan["end"]), "halt": plan["halt"], "new": new, "no_longer_live": gone, "duplicate_numbers": dup}
os.makedirs(OUT, exist_ok=True)
with open(LOG, "a") as fh: fh.write(json.dumps(rec, default=str) + "\n")
json.dump(state, open(STATE, "w"), indent=1)
print("sold rows %d | live %d (%d numbered) | would end now %d | new %d | %s" % (len(sold), rec["live"], len(idx), len(plan["end"]), len(new), plan["halt"]))
for e in new: print("  WOULD END", e["store"], e["item_id"], e["bravo_no"], e["title"][:50])
