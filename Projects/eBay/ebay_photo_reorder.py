#!/usr/bin/env python3
"""Reorder eBay listing photos (promote a whole-item shot to primary) for Roanoke.
Reads photo_reorder.json { ItemID: {title, old:[urls], new:[urls]} }.
Applies via ReviseFixedPriceItem PictureDetails (first URL = gallery/primary).
Reversible: state ~/ebay_photo_reorder_state.json { ItemID: old_order }.
Usage: python3 ebay_photo_reorder.py <reorder.json> [--apply|--revert] [--only ITEMID]"""
import json,os,sys,xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
from urllib.request import Request,urlopen
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.expanduser("~/.vp_secrets"))
from ebay_credentials import APP_ID as APP, DEV_ID as DEV, CERT_ID as CERT  # never hardcode these -- see ~/.vp_secrets/ebay_credentials.py
PATHS=[os.path.expanduser("~/ebay_weekly_rankings.py"),"/sessions/fervent-admiring-noether/mnt/Desktop/Claude/Claude Back Up/Claude 4 back up/ebay_weekly_rankings.py"]
NS="urn:ebay:apis:eBLBaseComponents";URL="https://api.ebay.com/ws/api.dll"
STATE=os.path.expanduser("~/ebay_photo_reorder_state.json")
def toks():
    for p in PATHS:
        if os.path.exists(p):
            ns={};exec(compile(open(p).read(),p,"exec"),ns)
            if "STORES" in ns: return {s["name"]:s["token"] for s in ns["STORES"]}
    raise SystemExit("no token")
def revise(t,iid,urls):
    pics="".join(f"<PictureURL>{escape(u)}</PictureURL>" for u in urls)
    body=(f'<?xml version="1.0" encoding="utf-8"?><ReviseFixedPriceItemRequest xmlns="urn:ebay:apis:eBLBaseComponents"><RequesterCredentials><eBayAuthToken>{t}</eBayAuthToken></RequesterCredentials><Item><ItemID>{iid}</ItemID><PictureDetails><GalleryType>Gallery</GalleryType>{pics}</PictureDetails></Item></ReviseFixedPriceItemRequest>').encode()
    h={"X-EBAY-API-SITEID":"0","X-EBAY-API-COMPATIBILITY-LEVEL":"967","X-EBAY-API-CALL-NAME":"ReviseFixedPriceItem","X-EBAY-API-APP-NAME":APP,"X-EBAY-API-DEV-NAME":DEV,"X-EBAY-API-CERT-NAME":CERT,"X-EBAY-API-IAF-TOKEN":t,"Content-Type":"text/xml"}
    r=ET.fromstring(urlopen(Request(URL,data=body,headers=h),timeout=90).read().decode())
    ack=r.findtext(f"{{{NS}}}Ack","")
    return ack in ("Success","Warning"),(r.findtext(f".//{{{NS}}}ShortMessage") or ack)
def main():
    data=json.load(open(sys.argv[1])); apply="--apply" in sys.argv; revert="--revert" in sys.argv
    only=None
    if "--only" in sys.argv: only=sys.argv[sys.argv.index("--only")+1]
    TK=toks(); state=json.load(open(STATE)) if os.path.exists(STATE) else {}
    if revert:
        for iid,rec in list(state.items()):
            if only and iid!=only: continue
            store=rec.get("store","Roanoke") if isinstance(rec,dict) else "Roanoke"
            old=rec["old"] if isinstance(rec,dict) else rec
            if apply:
                ok,msg=revise(TK[store],iid,old); print(("OK " if ok else "FAIL ")+iid,msg)
        return
    done=fail=0
    for iid,v in data.items():
        if only and iid!=only: continue
        store=v.get("store","Roanoke")
        if not apply: print(f"  {store} {iid}: primary -> pos moved  (n={len(v['new'])})"); continue
        ok,msg=revise(TK[store],iid,v['new'])
        if ok: state[iid]={"store":store,"old":v['old']}; done+=1; print("OK  ",store,iid,v['title'])
        else: fail+=1; print("FAIL",iid,msg)
    if apply: json.dump(state,open(STATE,"w"),indent=2); print(f"APPLIED {done}, failed {fail}")
if __name__=="__main__": main()
