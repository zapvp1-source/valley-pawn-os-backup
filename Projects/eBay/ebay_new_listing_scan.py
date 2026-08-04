#!/usr/bin/env python3
"""Valley Pawn -- pull NEW (last 7 days) eBay listings per store, with full picture URLs
and category info, for the weekly eBay quality-fix run.
ADDITIVE: new file, does not modify any existing eBay script.
Usage: python3 ebay_new_listing_scan.py <Store> <outpath.json> [--days N]
"""
import os, sys, json, time, xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen

sys.path.insert(0, os.path.expanduser("~/.vp_secrets"))
from ebay_credentials import APP_ID as APP, DEV_ID as DEV, CERT_ID as CERT

PATHS = [os.path.expanduser("~/ebay_weekly_rankings.py"),
         "/sessions/fervent-admiring-noether/mnt/Desktop/Claude/Claude Back Up/Claude 4 back up/ebay_weekly_rankings.py"]
NS = "urn:ebay:apis:eBLBaseComponents"
URL = "https://api.ebay.com/ws/api.dll"

def stores():
    for p in PATHS:
        if os.path.exists(p):
            ns = {}; exec(compile(open(p).read(), p, "exec"), ns)
            if "STORES" in ns: return ns["STORES"]
    raise SystemExit("no tokens")

def hdr(tok, name):
    return {"X-EBAY-API-SITEID":"0","X-EBAY-API-COMPATIBILITY-LEVEL":"967","X-EBAY-API-CALL-NAME":name,
            "X-EBAY-API-APP-NAME":APP,"X-EBAY-API-DEV-NAME":DEV,"X-EBAY-API-CERT-NAME":CERT,
            "X-EBAY-API-IAF-TOKEN":tok,"Content-Type":"text/xml"}

def parse_dt(s):
    if not s: return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
        try: return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError: continue
    return None

def active_ids(tok):
    out = []; page = 1
    while True:
        body = (f'<?xml version="1.0" encoding="utf-8"?><GetMyeBaySellingRequest xmlns="urn:ebay:apis:eBLBaseComponents">'
                f'<RequesterCredentials><eBayAuthToken>{tok}</eBayAuthToken></RequesterCredentials>'
                f'<ActiveList><Include>true</Include><Pagination><EntriesPerPage>200</EntriesPerPage>'
                f'<PageNumber>{page}</PageNumber></Pagination></ActiveList></GetMyeBaySellingRequest>').encode()
        r = ET.fromstring(urlopen(Request(URL, data=body, headers=hdr(tok, "GetMyeBaySelling")), timeout=60).read().decode())
        if r.findtext(f"{{{NS}}}Ack", "") == "Failure":
            msgs = r.findall(f".//{{{NS}}}ShortMessage")
            raise SystemExit("GetMyeBaySelling error: " + (msgs[0].text if msgs else "unknown"))
        for it in r.findall(f".//{{{NS}}}ActiveList/{{{NS}}}ItemArray/{{{NS}}}Item"):
            out.append({
                "id": it.findtext(f"{{{NS}}}ItemID"),
                "title": it.findtext(f"{{{NS}}}Title") or "",
                "cat_id": it.findtext(f".//{{{NS}}}PrimaryCategory/{{{NS}}}CategoryID"),
                "cat_name": it.findtext(f".//{{{NS}}}PrimaryCategory/{{{NS}}}CategoryName"),
                "start": it.findtext(f".//{{{NS}}}ListingDetails/{{{NS}}}StartTime"),
                "url": it.findtext(f".//{{{NS}}}ListingDetails/{{{NS}}}ViewItemURL") or "",
            })
        tp = r.findtext(f".//{{{NS}}}ActiveList/{{{NS}}}PaginationResult/{{{NS}}}TotalNumberOfPages")
        try: tp = int(tp)
        except (TypeError, ValueError): tp = page
        if page >= tp: break
        page += 1
    return out

def get_item_pics(tok, iid):
    body = (f'<?xml version="1.0" encoding="utf-8"?><GetItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">'
            f'<RequesterCredentials><eBayAuthToken>{tok}</eBayAuthToken></RequesterCredentials>'
            f'<ItemID>{iid}</ItemID><DetailLevel>ItemReturnAttributes</DetailLevel></GetItemRequest>').encode()
    r = ET.fromstring(urlopen(Request(URL, data=body, headers=hdr(tok, "GetItem")), timeout=60).read().decode())
    it = r.find(f".//{{{NS}}}Item")
    if it is None: return []
    return [p.text for p in it.findall(f".//{{{NS}}}PictureDetails/{{{NS}}}PictureURL")]

def main():
    store_name = sys.argv[1]; outpath = sys.argv[2]
    days = 7
    if "--days" in sys.argv:
        days = int(sys.argv[sys.argv.index("--days") + 1])
    tok = [s["token"] for s in stores() if s["name"].lower() == store_name.lower()][0]
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    all_items = active_ids(tok)
    new_items = []
    for it in all_items:
        st = parse_dt(it["start"])
        if st and st >= cutoff:
            new_items.append(it)
    print(f"{store_name}: {len(all_items)} active total, {len(new_items)} started in last {days} days", flush=True)
    for i, it in enumerate(new_items):
        try:
            it["pics"] = get_item_pics(tok, it["id"])
        except Exception as e:
            it["pics"] = []
            it["pics_err"] = str(e)
        time.sleep(0.15)
        if (i + 1) % 10 == 0:
            print(f"  ...{i+1}/{len(new_items)} fetched", flush=True)
    json.dump(new_items, open(outpath, "w"), indent=2)
    print(f"wrote {len(new_items)} new listings to {outpath}")

if __name__ == "__main__":
    main()
