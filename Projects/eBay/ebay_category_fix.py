#!/usr/bin/env python3
"""Valley Pawn -- reversible eBay PrimaryCategory revise for confirmed mismatches.
Input {id:{store,old_cat_id,old_cat_name,new_cat_id,new_cat_name}}.
State ~/ebay_category_fix_state.json {id:{store,old_cat_id}}.
Usage: ebay_category_fix.py <fixes.json> [--apply|--revert]
"""
import os, sys, json, xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

ns = {}; exec(compile(open(os.path.expanduser('~/ebay_weekly_rankings.py')).read(), 'x', 'exec'), ns)
TOK = {s['name']: s['token'] for s in ns['STORES']}
sys.path.insert(0, os.path.expanduser("~/.vp_secrets"))
from ebay_credentials import APP_ID as APP, DEV_ID as DEV, CERT_ID as CERT
NS = "urn:ebay:apis:eBLBaseComponents"
URL = "https://api.ebay.com/ws/api.dll"
STATE = os.path.expanduser('~/ebay_category_fix_state.json')

def hdr(tok, name):
    return {"X-EBAY-API-SITEID":"0","X-EBAY-API-COMPATIBILITY-LEVEL":"967","X-EBAY-API-CALL-NAME":name,
            "X-EBAY-API-APP-NAME":APP,"X-EBAY-API-DEV-NAME":DEV,"X-EBAY-API-CERT-NAME":CERT,
            "X-EBAY-API-IAF-TOKEN":tok,"Content-Type":"text/xml"}

def revise_cat(tok, iid, cat_id):
    b = (f'<?xml version="1.0" encoding="utf-8"?><ReviseFixedPriceItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">'
         f'<RequesterCredentials><eBayAuthToken>{tok}</eBayAuthToken></RequesterCredentials>'
         f'<Item><ItemID>{iid}</ItemID><PrimaryCategory><CategoryID>{cat_id}</CategoryID></PrimaryCategory></Item>'
         f'</ReviseFixedPriceItemRequest>').encode()
    r = ET.fromstring(urlopen(Request(URL, data=b, headers=hdr(tok, "ReviseFixedPriceItem")), timeout=60).read().decode())
    ack = r.findtext(f"{{{NS}}}Ack", "")
    return ack in ("Success", "Warning"), (r.findtext(f".//{{{NS}}}ShortMessage") or ack)

fixes = json.load(open(sys.argv[1]))
apply = "--apply" in sys.argv
state = json.load(open(STATE)) if os.path.exists(STATE) else {}

if "--revert" in sys.argv:
    for iid, rec in state.items():
        if apply:
            ok, m = revise_cat(TOK[rec['store']], iid, rec['old_cat_id'])
            print(("OK " if ok else "FAIL ") + iid, m)
    sys.exit()

for iid, v in fixes.items():
    if not apply:
        print("DRY", v['store'], iid, v['old_cat_name'], "->", v['new_cat_name']); continue
    ok, m = revise_cat(TOK[v['store']], iid, v['new_cat_id'])
    if ok:
        state[iid] = {"store": v['store'], "old_cat_id": v['old_cat_id'], "old_cat_name": v['old_cat_name']}
        print("OK  ", v['store'], iid, v['old_cat_name'], "->", v['new_cat_name'])
    else:
        print("FAIL", iid, m)
if apply:
    json.dump(state, open(STATE, 'w'), indent=2)
