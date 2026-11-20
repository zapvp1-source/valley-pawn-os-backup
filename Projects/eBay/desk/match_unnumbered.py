#!/usr/bin/env python3
"""Read-only. For eBay sold lines with no Bravo number (shadow output), find the Bravo sale
that matches by store + date window + price + description words. Writes out/unnumbered_match_<tag>.csv.
No network, no eBay or Bravo writes. Usage: match_unnumbered.py <shadow.json>"""
import csv, glob, json, os, re, sys
from datetime import datetime, timedelta
P = os.path.expanduser("~/Documents/Claude/Projects")
if not os.path.isdir(P): P = os.path.join(os.environ["HOME"], "mnt", "Projects")
SOLD = os.path.join(P, "Bravo Data Extraction", "output")
CODE = {"Culpeper": "CUL", "Waynesboro": "WAY", "Harrisonburg": "HAR", "Lexington": "LEX", "Roanoke": "ROA"}
STOP = set("the a an and or with w for of in on to new used video game games console sealed box lot".split())
def words(s):
    s = s.lower().replace("playstation", "ps").replace("nintendo", "").replace("sony", "")
    return {w for w in re.findall(r"[a-z0-9]+", s) if len(w) > 1 and w not in STOP}
def money(s):
    try: return abs(float(re.sub(r"[^0-9.\-]", "", s or "") or 0))
    except ValueError: return 0.0
def load(code):
    rows = []
    for f in glob.glob(os.path.join(SOLD, "*_%s_sold-discount-detail.csv" % code)):
        for r in csv.DictReader(open(f, newline="", encoding="utf-8", errors="ignore")):
            if (r.get("Status") or "").upper() != "SOLD": continue
            try: d = datetime.strptime(r["Date"].strip(), "%m/%d/%Y").date()
            except Exception: continue
            rows.append({"num": r["Number"].strip(), "desc": r["Description"], "cat": r.get("Category", ""),
                         "price": money(r.get("Last Sold Price")), "date": d})
    seen = {}; [seen.setdefault((x["num"], x["date"]), x) for x in rows]
    return list(seen.values())
def main(path):
    data = json.load(open(path))
    lines = data if isinstance(data, list) else next(v for v in data.values() if isinstance(v, list))
    todo = [l for l in lines if not l.get("bravo_no")]
    cache, used, out = {}, set(), []
    for l in sorted(todo, key=lambda x: x["paid_utc"]):
        code = CODE[l["store"]]; cand = cache.setdefault(code, load(code))
        paid = datetime.fromisoformat(l["paid_utc"].replace("Z", "+00:00")).date()
        price = float(l["ring_price"]); tw = words(l["title"]); scored = []
        for c in cand:
            if (c["num"], c["date"]) in used: continue
            lag = (c["date"] - paid).days
            if lag < -1 or lag > 10: continue
            pgap = abs(c["price"] - price) / max(price, 1)
            ov = len(tw & words(c["desc"] + " " + c["cat"])) / max(1, min(len(tw), 6))
            if pgap > 0.25 and ov < 0.5: continue
            score = ov * 2 + max(0, 1 - pgap * 4) + max(0, 1 - abs(lag) / 10)
            scored.append((score, ov, pgap, lag, c))
        scored.sort(key=lambda x: -x[0])
        best = scored[0] if scored else None
        second = scored[1][0] if len(scored) > 1 else 0
        if best and best[0] >= 2.0 and best[0] - second >= 0.5:
            verdict = "match"; used.add((best[4]["num"], best[4]["date"]))
        elif best and best[0] >= 1.3: verdict = "likely - check"
        else: verdict = "no match"
        out.append([l["store"], l["paid_utc"][:10], "%.2f" % price, l["title"][:70], verdict,
                    best[4]["num"] if best else "", best[4]["desc"][:40] if best else "",
                    "%.2f" % best[4]["price"] if best else "", str(best[4]["date"]) if best else "",
                    "%.2f" % best[0] if best else ""])
    tag = os.path.basename(path).replace("shadow_", "").rsplit(".", 1)[0]
    dst = os.path.join(os.path.dirname(path), "unnumbered_match_%s.csv" % tag)
    with open(dst, "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["store", "paid", "ebay_price", "ebay_title", "verdict", "bravo_no", "bravo_desc", "bravo_price", "bravo_date", "score"]); w.writerows(out)
    from collections import Counter
    c = Counter((r[0], r[4]) for r in out)
    for s in CODE:
        print(s, {v: c[(s, v)] for v in ("match", "likely - check", "no match") if c[(s, v)]})
    print("total", Counter(r[4] for r in out)); print("->", dst)
    return out
if __name__ == "__main__":
    for r in main(sys.argv[1]): print(" | ".join(r[:9]))
