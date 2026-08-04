#!/usr/bin/env python3
"""Valley Pawn -- analyze NEW listings (from new_listings_<Store>.json) for weak titles
and category mismatches via eBay Taxonomy API. Writes analysis_report.json.
ADDITIVE: new file, does not modify any existing eBay script.
"""
import os, sys, json, base64, urllib.parse, xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

sys.path.insert(0, os.path.expanduser("~/.vp_secrets"))
from ebay_credentials import APP_ID as APP, DEV_ID as DEV, CERT_ID as CERT

PATHS = [os.path.expanduser("~/ebay_weekly_rankings.py")]
NS = "urn:ebay:apis:eBLBaseComponents"
URL = "https://api.ebay.com/ws/api.dll"

def stores():
    for p in PATHS:
        if os.path.exists(p):
            ns = {}; exec(compile(open(p).read(), p, "exec"), ns)
            if "STORES" in ns: return {s["name"]: s["token"] for s in ns["STORES"]}
    raise SystemExit("no tokens")

def hdr(tok, name):
    return {"X-EBAY-API-SITEID":"0","X-EBAY-API-COMPATIBILITY-LEVEL":"967","X-EBAY-API-CALL-NAME":name,
            "X-EBAY-API-APP-NAME":APP,"X-EBAY-API-DEV-NAME":DEV,"X-EBAY-API-CERT-NAME":CERT,
            "X-EBAY-API-IAF-TOKEN":tok,"Content-Type":"text/xml"}

def get_item_cat(tok, iid):
    body = (f'<?xml version="1.0" encoding="utf-8"?><GetItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">'
            f'<RequesterCredentials><eBayAuthToken>{tok}</eBayAuthToken></RequesterCredentials>'
            f'<ItemID>{iid}</ItemID><DetailLevel>ItemReturnAttributes</DetailLevel></GetItemRequest>').encode()
    r = ET.fromstring(urlopen(Request(URL, data=body, headers=hdr(tok, "GetItem")), timeout=60).read().decode())
    it = r.find(f".//{{{NS}}}Item")
    if it is None: return None, None
    return (it.findtext(f".//{{{NS}}}PrimaryCategory/{{{NS}}}CategoryID"),
            it.findtext(f".//{{{NS}}}PrimaryCategory/{{{NS}}}CategoryName"))

def app_token():
    a = base64.b64encode(f"{APP}:{CERT}".encode()).decode()
    d = urllib.parse.urlencode({"grant_type": "client_credentials", "scope": "https://api.ebay.com/oauth/api_scope"}).encode()
    return json.load(urlopen(Request("https://api.ebay.com/identity/v1/oauth2/token", data=d,
        headers={"Authorization": f"Basic {a}", "Content-Type": "application/x-www-form-urlencoded"}), timeout=30))["access_token"]

def suggest(at, q):
    url = "https://api.ebay.com/commerce/taxonomy/v1/category_tree/0/get_category_suggestions?" + urllib.parse.urlencode({"q": q[:300]})
    try:
        j = json.load(urlopen(Request(url, headers={"Authorization": f"Bearer {at}"}), timeout=20))
        s = j["categorySuggestions"][0]; cat = s["category"]
        path = " > ".join(a["categoryName"] for a in s.get("categoryTreeNodeAncestors", [])[::-1])
        return cat["categoryId"], cat["categoryName"], path
    except Exception:
        return None, None, None

def is_weak_title(title):
    # weak: short, or few distinct words, or looks like model-number-only
    words = title.split()
    if len(title) < 40: return True
    if len(words) <= 3: return True
    return False

def main():
    stores_map = stores()
    at = app_token()
    report = []
    for store in ["Culpeper", "Waynesboro", "Harrisonburg", "Lexington", "Roanoke"]:
        path = f"new_listings_{store}.json"
        if not os.path.exists(path): continue
        items = json.load(open(path))
        tok = stores_map.get(store)
        for it in items:
            cat_id, cat_name = get_item_cat(tok, it["id"])
            sug_id, sug_name, sug_path = suggest(at, it["title"])
            mismatch = bool(sug_id and cat_id and sug_id != cat_id)
            report.append({
                "store": store, "id": it["id"], "title": it["title"],
                "title_len": len(it["title"]), "n_pics": len(it.get("pics", [])),
                "cat_id": cat_id, "cat_name": cat_name,
                "sug_cat_id": sug_id, "sug_cat_name": sug_name, "sug_cat_path": sug_path,
                "cat_mismatch": mismatch,
                "weak_title": is_weak_title(it["title"]),
                "url": it.get("url", ""),
                "first_pic": (it.get("pics") or [None])[0],
                "pics": it.get("pics", []),
            })
    json.dump(report, open("analysis_report.json", "w"), indent=2)
    print(f"wrote {len(report)} rows to analysis_report.json")
    for r in report:
        flags = []
        if r["weak_title"]: flags.append("WEAK-TITLE")
        if r["cat_mismatch"]: flags.append(f"CAT-MISMATCH({r['cat_name']}->{r['sug_cat_name']})")
        print(f"{r['store']:14s} {r['id']} len={r['title_len']:3d} pics={r['n_pics']:2d} {' '.join(flags):50s} {r['title']}")

if __name__ == "__main__":
    main()
