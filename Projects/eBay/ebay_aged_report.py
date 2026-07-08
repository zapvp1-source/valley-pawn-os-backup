#!/usr/bin/env python3
"""
Valley Pawn — eBay Aged-Inventory Report (item-level, per store)
Pulls every ACTIVE listing older than N days (default 90) with detail, per store.
Reuses tokens from ebay_weekly_rankings.py. Writes JSON to --out.

Usage: python3 ebay_aged_report.py --days 90 --out aged.json [--stores Culpeper,Roanoke]
"""
import argparse
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen

import sys as _sys, os as _os
_sys.path.insert(0, _os.path.expanduser("~/.vp_secrets"))
from ebay_credentials import APP_ID, DEV_ID, CERT_ID  # never hardcode these -- see ~/.vp_secrets/ebay_credentials.py
RANKINGS_PATHS = [
    os.path.expanduser("~/ebay_weekly_rankings.py"),
    "/sessions/fervent-admiring-noether/mnt/Desktop/Claude/Claude Back Up/Claude 4 back up/ebay_weekly_rankings.py",
    os.path.expanduser("~/Desktop/Claude/Claude Back Up/Claude 4 back up/ebay_weekly_rankings.py"),
]
NS = "urn:ebay:apis:eBLBaseComponents"
EBAY_URL = "https://api.ebay.com/ws/api.dll"


def load_stores():
    for p in RANKINGS_PATHS:
        if os.path.exists(p):
            ns = {}
            exec(compile(open(p).read(), p, "exec"), ns)
            if "STORES" in ns:
                return ns["STORES"]
    raise SystemExit("no rankings script found")


def _active_page(token, page):
    body = (f'<?xml version="1.0" encoding="utf-8"?>'
            f'<GetMyeBaySellingRequest xmlns="urn:ebay:apis:eBLBaseComponents">'
            f'<RequesterCredentials><eBayAuthToken>{token}</eBayAuthToken></RequesterCredentials>'
            f'<ActiveList><Include>true</Include>'
            f'<Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>{page}</PageNumber></Pagination>'
            f'</ActiveList></GetMyeBaySellingRequest>').encode()
    headers = {"X-EBAY-API-SITEID": "0", "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
               "X-EBAY-API-CALL-NAME": "GetMyeBaySelling", "X-EBAY-API-APP-NAME": APP_ID,
               "X-EBAY-API-DEV-NAME": DEV_ID, "X-EBAY-API-CERT-NAME": CERT_ID,
               "X-EBAY-API-IAF-TOKEN": token, "Content-Type": "text/xml"}
    with urlopen(Request(EBAY_URL, data=body, headers=headers), timeout=90) as r:
        return ET.fromstring(r.read().decode())


def parse_dt(s):
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue
    return None


def aged_for_store(store, cutoff, now):
    token = store["token"]
    items = []
    page = 1
    while True:
        root = _active_page(token, page)
        if root.findtext(f"{{{NS}}}Ack", "") == "Failure":
            break
        for it in root.findall(f".//{{{NS}}}ActiveList/{{{NS}}}ItemArray/{{{NS}}}Item"):
            st = parse_dt(it.findtext(f".//{{{NS}}}ListingDetails/{{{NS}}}StartTime") or "")
            if not st or st >= cutoff:
                continue
            price = (it.findtext(f".//{{{NS}}}SellingStatus/{{{NS}}}CurrentPrice")
                     or it.findtext(f".//{{{NS}}}BuyItNowPrice")
                     or it.findtext(f".//{{{NS}}}StartPrice") or "0")
            try:
                price = float(price)
            except ValueError:
                price = 0.0
            watch = it.findtext(f".//{{{NS}}}WatchCount") or "0"
            items.append({
                "item_id": it.findtext(f"{{{NS}}}ItemID") or "",
                "title": it.findtext(f"{{{NS}}}Title") or "",
                "price": price,
                "start": st.strftime("%Y-%m-%d"),
                "days_aged": (now - st).days,
                "watchers": int(watch) if watch.isdigit() else 0,
                "url": it.findtext(f".//{{{NS}}}ListingDetails/{{{NS}}}ViewItemURL") or "",
            })
        tp = root.findtext(f".//{{{NS}}}ActiveList/{{{NS}}}PaginationResult/{{{NS}}}TotalNumberOfPages")
        try:
            tp = int(tp)
        except (TypeError, ValueError):
            tp = page
        if page >= tp:
            break
        page += 1
    items.sort(key=lambda x: x["days_aged"], reverse=True)
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--out", default="aged.json")
    ap.add_argument("--stores", default="")
    args = ap.parse_args()
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=args.days)
    want = [s.strip().lower() for s in args.stores.split(",") if s.strip()]
    result = {}
    for s in load_stores():
        if want and s["name"].lower() not in want:
            continue
        items = aged_for_store(s, cutoff, now)
        result[s["name"]] = items
        print(f"{s['name']}: {len(items)} aged >{args.days}d, ${sum(i['price'] for i in items):,.2f}")
    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
