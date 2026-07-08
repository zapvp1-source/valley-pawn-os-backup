#!/usr/bin/env python3
"""Bulk-end eBay listings from a JSON list [{store,id,title}].
Ends via EndFixedPriceItem (reason NotAvailable). Records results to ~/ebay_delist_record.json.
Usage: ebay_end_bulk.py <list.json> [--apply]"""
import os,sys,json,time,xml.etree.ElementTree as ET
from urllib.request import Request,urlopen
ns={}; exec(compile(open(os.path.expanduser('~/ebay_weekly_rankings.py')).read(),'x','exec'),ns)
TOK={s['name']:s['token'] for s in ns['STORES']}
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.expanduser("~/.vp_secrets"))
from ebay_credentials import APP_ID as APP, DEV_ID as DEV, CERT_ID as CERT  # never hardcode these -- see ~/.vp_secrets/ebay_credentials.py
NS="urn:ebay:apis:eBLBaseComponents";URL="https://api.ebay.com/ws/api.dll"
REC=os.path.expanduser("~/ebay_delist_record.json")
def end(tok,iid):
    b=f'<?xml version="1.0"?><EndFixedPriceItemRequest xmlns="urn:ebay:apis:eBLBaseComponents"><RequesterCredentials><eBayAuthToken>{tok}</eBayAuthToken></RequesterCredentials><ItemID>{iid}</ItemID><EndingReason>NotAvailable</EndingReason></EndFixedPriceItemRequest>'
    h={"X-EBAY-API-SITEID":"0","X-EBAY-API-COMPATIBILITY-LEVEL":"967","X-EBAY-API-CALL-NAME":"EndFixedPriceItem","X-EBAY-API-APP-NAME":APP,"X-EBAY-API-DEV-NAME":DEV,"X-EBAY-API-CERT-NAME":CERT,"X-EBAY-API-IAF-TOKEN":tok,"Content-Type":"text/xml"}
    r=ET.fromstring(urlopen(Request(URL,data=b.encode(),headers=h),timeout=60).read().decode())
    ack=r.findtext(f"{{{NS}}}Ack")
    msg=r.findtext(f".//{{{NS}}}ShortMessage") or ""
    return ack,msg
items=json.load(open(sys.argv[1])); apply="--apply" in sys.argv
rec=json.load(open(REC)) if os.path.exists(REC) else {}
done=fail=skip=0
for it in items:
    iid=it["id"]
    if iid in rec: skip+=1; continue
    if not apply: print("DRY",it["store"],iid,it["title"][:40]); continue
    try:
        ack,msg=end(TOK[it["store"]],iid)
        if ack in ("Success","Warning"):
            rec[iid]={"store":it["store"],"title":it["title"]}; done+=1
            print("OK  ",it["store"],iid,it["title"][:40],flush=True)
        else:
            fail+=1; print("FAIL",it["store"],iid,msg,flush=True)
    except Exception as e:
        fail+=1; print("ERR ",iid,e,flush=True)
    json.dump(rec,open(REC,"w"),indent=2); time.sleep(0.3)
print(f"{'APPLIED' if apply else 'DRY'} ended={done} failed={fail} skipped={skip}")
