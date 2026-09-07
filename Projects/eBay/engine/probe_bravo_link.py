#!/usr/bin/env python3
"""READ-ONLY probe: how are eBay listings linked to Bravo today?

Per store: active count, titles carrying a Bravo intake code "(VAP…)", SKU populated,
codes recoverable from the title-stripper's state file (original titles), and a GetItem
sample showing SKU / ApplicationData / PrivateNotes for a few Bravo-created listings.
Writes engine/data/probe_bravo_link_<date>.json. No eBay writes.
"""
import json, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ebay_common import *  # noqa

TITLE_STATE = os.path.expanduser("~/ebay_title_state.json")
state = json.load(open(TITLE_STATE)) if os.path.exists(TITLE_STATE) else {}

report = {"date": time.strftime("%Y-%m-%d"), "stores": {}}
for store in STORE_ORDER:
    tok = token_for(store)
    items = active_items(tok)
    n = len(items)
    with_code = [i for i in items if CODE_RE.search(i["Title"])]
    sku_set = [i for i in items if i["SKU"].strip()]
    recoverable = [i for i in items if not CODE_RE.search(i["Title"]) and i["ItemID"] in state
                   and CODE_RE.search(state[i["ItemID"]].get("original", ""))]
    neither = [i for i in items if not CODE_RE.search(i["Title"]) and i["ItemID"] not in state and not i["SKU"].strip()]
    sample = []
    for i in (with_code[:2] + recoverable[:1] + neither[:1]):
        r, err = get_item(tok, i["ItemID"])
        if r is None:
            sample.append({"ItemID": i["ItemID"], "error": err}); continue
        sample.append({
            "ItemID": i["ItemID"], "Title": t(r, "Title"), "SKU": t(r, "SKU"),
            "ApplicationData": t(r, "ApplicationData"), "PrivateNotes": t(r, "PrivateNotes"),
            "InventoryTrackingMethod": t(r, "InventoryTrackingMethod"),
            "ListingType": t(r, "ListingType"), "StartTime": t(r, "StartTime"),
        })
    rep = {"active": n, "title_has_code": len(with_code), "sku_set": len(sku_set),
           "code_recoverable_from_state": len(recoverable), "no_code_no_state_no_sku": len(neither),
           "sample": sample}
    report["stores"][store] = rep
    print("%-12s active %3d | title code %3d | SKU set %3d | recoverable %3d | unlinked %3d"
          % (store, n, len(with_code), len(sku_set), len(recoverable), len(neither)))
    for s in sample:
        print("   ", json.dumps(s, ensure_ascii=False)[:300])

os.makedirs(DATA_DIR, exist_ok=True)
out = os.path.join(DATA_DIR, "probe_bravo_link_%s.json" % report["date"])
json.dump(report, open(out, "w"), indent=2)
print("saved", out)
