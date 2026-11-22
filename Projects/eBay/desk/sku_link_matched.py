#!/usr/bin/env python3
"""Write Bravo numbers into SKU for live eBay listings matched by match_live_unnumbered.py (Joshua approved SKU writes 11/19).
Accepts 'match' rows, and 'possible' rows only when they share a model-number token (letters+digits, 4+ chars).
Skips any Bravo number already on another live listing. Only empty SKUs. Ledger: engine/ledger.jsonl (revert with
engine/sku_link.py --revert <run_id> --apply). Usage: sku_link_matched.py <csv> [--apply]"""
import csv, os, re, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "engine")); sys.path.insert(0, HERE)
import ebay_common as ec, desk_core as dc
from xml.sax.saxutils import escape
rows = list(csv.DictReader(open(sys.argv[1]))); apply = "--apply" in sys.argv
def model_tokens(s): return {t for t in re.findall(r"[a-z0-9\-]+", s.lower().replace("-", "")) if len(t) >= 4 and re.search(r"\d", t) and re.search(r"[a-z]", t)}
live = {s: ec.active_items(ec.token_for(s)) for s in ec.STORE_ORDER}
used = {dc.bravo_code(i["SKU"], i["Title"]) for v in live.values() for i in v} - {""}
empty = {i["ItemID"] for v in live.values() for i in v if not i["SKU"].strip()}
plan, skip = [], []
seen = set()
for r in rows:
    ok = r["verdict"] == "match" or (r["verdict"] == "possible" and model_tokens(r["ebay_title"]) & model_tokens(r["bravo_desc"]))
    if not ok: continue
    b = r["bravo_no"]
    if b in used or b in seen or r["item_id"] not in empty: skip.append((r["item_id"], b, "in use/dup/not empty")); continue
    seen.add(b); plan.append((r["store"], r["item_id"], b))
print("plan %d, skipped %d" % (len(plan), len(skip)))
run_id = time.strftime("%Y%m%d-%H%M%S") + "-skulink-matched"; ok = fail = 0
if apply:
    for store, iid, b in plan:
        good, err = ec.revise(ec.token_for(store), iid, "<SKU>%s</SKU>" % escape(b))
        ec.ledger_append({"run_id": run_id, "store": store, "ItemID": iid, "action": "sku_set", "before": "", "after": b,
                          "source": "match_live_unnumbered", "ok": good, "err": [e[1] for e in err][:1] if not good else []})
        ok += good; fail += (not good)
        if not good: print("FAIL", store, iid, err[:1])
        time.sleep(0.2)
    print("run_id=%s applied=%d failed=%d" % (run_id, ok, fail))
from collections import Counter
print(Counter(p[0] for p in plan))
