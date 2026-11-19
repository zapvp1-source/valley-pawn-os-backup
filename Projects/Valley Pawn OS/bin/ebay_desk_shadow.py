#!/usr/bin/env python3
"""ebay_desk_shadow.py [days] — eBay Desk gate 1: READ-ONLY shadow (Joshua OK 2026-11-18).

Pulls orders from the 5 store eBay accounts with ONE Trading API call name, GetOrders (a read), and
compares them with Bravo's daily sold exports already on disk. It writes two files under
Projects/eBay/desk/out/ and nothing else: no eBay write call, no Bravo touch, no Slack, no email.
The only call name this file can send is the constant below.
"""
import csv, glob, json, os, sys, time
from datetime import datetime, timedelta, timezone
P = os.path.expanduser("~/Documents/Claude/Projects")
sys.path.insert(0, os.path.join(P, "eBay", "engine")); sys.path.insert(0, os.path.join(P, "eBay", "desk"))
import ebay_common as ec
import desk_core as dc

READ_CALL = "GetOrders"
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 21
OUT = os.path.join(P, "eBay", "desk", "out"); os.makedirs(OUT, exist_ok=True)
NOW = datetime.now(timezone.utc)
FROM = NOW - timedelta(days=DAYS)
REC = os.path.join(P, "eBay", "engine", "data", "recoverable_codes.json")
recoverable = json.load(open(REC)) if os.path.exists(REC) else {}


def pull(store):
    tok = ec.token_for(store); page = 1; lines = []; n_orders = 0
    while True:
        inner = ("<CreateTimeFrom>%s</CreateTimeFrom><CreateTimeTo>%s</CreateTimeTo><OrderRole>Seller</OrderRole>"
                 "<OrderStatus>All</OrderStatus><Pagination><EntriesPerPage>100</EntriesPerPage><PageNumber>%d</PageNumber></Pagination>"
                 % (FROM.strftime("%Y-%m-%dT%H:%M:%S.000Z"), NOW.strftime("%Y-%m-%dT%H:%M:%S.000Z"), page))
        r = ec.call(tok, READ_CALL, inner)
        if not ec.ack_ok(r):
            raise RuntimeError("%s %s: %s" % (READ_CALL, store, ec.errors(r)[:2]))
        import xml.etree.ElementTree as ET
        n_orders += len(r.findall(".//{%s}Order" % ec.NS))
        lines += dc.parse_get_orders(ET.tostring(r, encoding="unicode"), store)
        if (r.findtext("{%s}HasMoreOrders" % ec.NS) or "false").lower() != "true" or page >= 50:
            break
        page += 1
    for ln in lines:                       # titles the stripper cleaned: recover the Bravo number by ItemID
        if not ln["bravo_no"]:
            c = (recoverable.get(ln["item_id"]) or [None])[0]
            if c and dc.BARE_CODE_RE.match(str(c).upper()):
                ln["bravo_no"] = str(c).upper(); ln["code_source"] = "state"
    return n_orders, lines


def main():
    res = {"generated_utc": NOW.isoformat(), "days": DAYS, "stores": {}, "lines": []}
    sold_files = glob.glob(os.path.join(P, "Bravo Data Extraction", "output", "*_sold-discount-detail.csv"))
    sold = dc.load_bravo_sold(sold_files)      # an item can be rung at any store; match all stores' exports
    for store in ec.STORE_ORDER:
        code = dc.STORE_CODE[store]
        try:
            n_orders, lines = pull(store)
        except Exception as e:
            res["stores"][store] = {"error": str(e)[:200]}; continue
        checked = dc.check_rung(dc.build_ring_queue(lines), sold, NOW)
        lags = []
        for r in checked:
            if r["state"] == "rung":
                paid_et = (datetime.fromisoformat(r["paid_utc"]) - timedelta(hours=5)).date()
                r["lag_days"] = (datetime.fromisoformat(r["bravo_sold_date"]).date() - paid_et).days
                lags.append(r["lag_days"])
            r.pop("buyer", None)
        s = dc.store_summary(checked).get(store, {})
        s.update({"orders_returned": n_orders, "lines": len(checked), "sales_dollars": round(sum(r["ring_price"] for r in checked), 2),
                  "rung_same_or_next_day": sum(1 for l in lags if l <= 1), "rung_late": sum(1 for l in lags if l > 1),
                  "sold_files_for_store": len([f for f in sold_files if "_%s_" % code in f])})
        res["stores"][store] = s; res["lines"] += checked
        time.sleep(1)
    tag = NOW.strftime("%Y-%m-%d_%H%M")
    json.dump(res, open(os.path.join(OUT, "shadow_%s.json" % tag), "w"), indent=1)
    with open(os.path.join(OUT, "shadow_%s.csv" % tag), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["store", "paid_utc", "state", "bravo_no", "ring_price", "bravo_sold_date", "lag_days", "price_gap", "item_id", "title"])
        for r in res["lines"]:
            w.writerow([r["store"], r["paid_utc"], r["state"], r["bravo_no"], r["ring_price"], r.get("bravo_sold_date", ""), r.get("lag_days", ""), r.get("price_gap", ""), r["item_id"], r["title"]])
    print(json.dumps(res["stores"], indent=1))


if __name__ == "__main__":
    main()
