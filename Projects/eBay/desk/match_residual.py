#!/usr/bin/env python3
"""READ-ONLY. Residual match: live eBay listings still without a Bravo number vs Bravo's eBay-marked items
(ebay-listed CSVs) that are not yet on any live listing. Same store only. Prints candidates."""
import csv, glob, os, re, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import ebay_common as ec, desk_core as dc
from match_unnumbered import money, CODE
def toks(s):
    s = s.lower().replace("playstation", "ps").replace("&", " ")
    return {w for w in re.findall(r"[a-z0-9]+", s) if len(w) > 1}
res = []
for store in ec.STORE_ORDER:
    live = ec.active_items(ec.token_for(store))
    used = {dc.bravo_code(i["SKU"], i["Title"]) for i in live} - {""}
    un = [i for i in live if not dc.bravo_code(i["SKU"], i["Title"])]
    f = sorted(glob.glob(os.path.join(HERE, "out", "bravo_pulls", "*_%s_ebay-listed.csv" % CODE[store])))[-1]
    cand = [r for r in csv.DictReader(open(f, encoding="utf-8", errors="ignore")) if r["Number"].strip().upper() not in used]
    print("%s: unnumbered live %d | Bravo eBay-marked not on a listing %d" % (store, len(un), len(cand)))
    for i in un:
        tw = toks(i["Title"]); p = money(i["StartPrice"]); sc = []
        for c in cand:
            cw = toks(c["Description"] + " " + c["Category"]); ov = len(tw & cw)
            cp = money(c["Price"]); pg = abs(cp - p) / max(p, 1)
            sc.append((ov + (2 if pg < 0.005 else 1 if pg < 0.12 else 0), ov, round(pg, 2), c))
        sc.sort(key=lambda x: -x[0]); top = sc[:2]
        res.append({"store": store, "item_id": i["ItemID"], "title": i["Title"], "price": p,
                    "cands": [{"no": t[3]["Number"], "desc": t[3]["Description"], "cat": t[3]["Category"], "price": t[3]["Price"], "ov": t[1], "pg": t[2], "score": t[0]} for t in top]})
json.dump(res, open(os.path.join(HERE, "out", "residual_candidates.json"), "w"), indent=1)
for r in res:
    c = r["cands"]; a = c[0] if c else None
    print("%s %s $%.2f %s" % (r["store"][:3], r["item_id"], r["price"], r["title"][:62]))
    for x in c: print("      -> %s %s | %s | %s (ov %d, pg %.2f)" % (x["no"], x["price"], x["cat"][:18], x["desc"][:34], x["ov"], x["pg"]))
