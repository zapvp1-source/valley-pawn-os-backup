#!/usr/bin/env python3
"""READ-ONLY. Live eBay listings with no Bravo number -> best Bravo inventory match from exports on disk
(markdown-verification INVENTORY rows, items-to-price, inventory-details). Writes out/live_unnumbered_match_<tag>.csv."""
import csv, glob, os, re, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import ebay_common as ec, desk_core as dc
from match_unnumbered import words, money, CODE
OUT = os.path.join(HERE, "..", "..", "Bravo Data Extraction", "output")
def bravo_items(code):
    items = {}
    for pat in ("*_%s_markdown-verification.csv", "*_%s_items-to-price.csv", "*_%s_inventory-details.csv"):
        for f in sorted(glob.glob(os.path.join(OUT, pat % code))):
            for r in csv.DictReader(open(f, newline="", encoding="utf-8", errors="ignore")):
                n = (r.get("Number") or "").strip().upper()
                if not n or (r.get("Status") or "").upper() == "SOLD": continue
                items[n] = {"num": n, "desc": r.get("Description", ""), "cat": r.get("Category", ""), "price": money(r.get("Price")), "src": os.path.basename(f)[-28:]}
    return list(items.values())
rows = []
for store in ec.STORE_ORDER:
    cand = bravo_items(CODE[store])
    for it in ec.active_items(ec.token_for(store)):
        if dc.bravo_code(it["SKU"], it["Title"]): continue
        tw = words(it["Title"]); price = money(it["StartPrice"]); best = []
        for c in cand:
            ov = len(tw & words(c["desc"] + " " + c["cat"])) / max(1, min(len(tw), 6))
            if ov < 0.34: continue
            pg = abs(c["price"] - price) / max(price, 1) if c["price"] else 1
            best.append((ov * 2 + max(0, 1 - pg * 2), ov, c))
        best.sort(key=lambda x: -x[0]); b = best[0] if best else None
        sec = best[1][0] if len(best) > 1 else 0
        v = "match" if b and b[0] >= 2.0 and b[0] - sec >= 0.5 else ("possible" if b and b[0] >= 1.2 else "none")
        rows.append([store, it["ItemID"], it["Title"][:70], "%.2f" % price, (it["StartTime"] or "")[:10], v,
                     b[2]["num"] if b else "", b[2]["desc"][:40] if b else "", "%.2f" % b[2]["price"] if b else "", "%.2f" % b[0] if b else "", len(cand)])
dst = os.path.join(HERE, "out", "live_unnumbered_match_%s.csv" % time.strftime("%Y-%m-%d_%H%M"))
with open(dst, "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["store", "item_id", "ebay_title", "ebay_price", "listed", "verdict", "bravo_no", "bravo_desc", "bravo_price", "score", "bravo_items_on_file"]); w.writerows(rows)
from collections import Counter
print(Counter((r[0], r[5]) for r in rows)); print(Counter(r[4][:7] for r in rows)); print("->", dst)
